import datetime
from dateutil.relativedelta import relativedelta

from django.core.validators import ValidationError, RegexValidator
from django.db import models
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.template import loader, Context
from django.utils import timezone, translation
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.accounts.models import Account
from orchestra.contrib.contacts.models import Contact
from orchestra.core import accounts, validators
from orchestra.utils.html import html_to_pdf

from . import settings


class BillContact(models.Model):
    account = models.OneToOneField('accounts.Account', verbose_name=_("account"),
        related_name='billcontact')
    name = models.CharField(_("name"), max_length=256, blank=True,
        help_text=_("Account full name will be used when left blank."))
    address = models.TextField(_("address"))
    city = models.CharField(_("city"), max_length=128,
        default=settings.BILLS_CONTACT_DEFAULT_CITY)
    zipcode = models.CharField(_("zip code"), max_length=10,
        validators=[RegexValidator(r'^[0-9A-Z]{3,10}$', _("Enter a valid zipcode."))])
    country = models.CharField(_("country"), max_length=20,
        choices=settings.BILLS_CONTACT_COUNTRIES,
        default=settings.BILLS_CONTACT_DEFAULT_COUNTRY)
    vat = models.CharField(_("VAT number"), max_length=64)
    
    def __str__(self):
        return self.name
    
    def get_name(self):
        return self.name or self.account.get_full_name()
    
    def clean(self):
        self.vat = self.vat.strip()
        self.city = self.city.strip()
        validators.all_valid({
            'vat': (validators.validate_vat, self.vat, self.country),
            'zipcode': (validators.validate_zipcode, self.zipcode, self.country)
        })


class BillManager(models.Manager):
    def get_queryset(self):
        queryset = super(BillManager, self).get_queryset()
        if self.model != Bill:
            bill_type = self.model.get_class_type()
            queryset = queryset.filter(type=bill_type)
        return queryset


class Bill(models.Model):
    OPEN = ''
    PAID = 'PAID'
    PENDING = 'PENDING'
    BAD_DEBT = 'BAD_DEBT'
    PAYMENT_STATES = (
        (PAID, _("Paid")),
        (PENDING, _("Pending")),
        (BAD_DEBT, _("Bad debt")),
    )
    BILL = 'BILL'
    INVOICE = 'INVOICE'
    AMENDMENTINVOICE = 'AMENDMENTINVOICE'
    FEE = 'FEE'
    AMENDMENTFEE = 'AMENDMENTFEE'
    PROFORMA = 'PROFORMA'
    TYPES = (
        (INVOICE, _("Invoice")),
        (AMENDMENTINVOICE, _("Amendment invoice")),
        (FEE, _("Fee")),
        (AMENDMENTFEE, _("Amendment Fee")),
        (PROFORMA, _("Pro forma")),
    )
    
    number = models.CharField(_("number"), max_length=16, unique=True, blank=True)
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
         related_name='%(class)s')
    type = models.CharField(_("type"), max_length=16, choices=TYPES)
    created_on = models.DateField(_("created on"), auto_now_add=True)
    closed_on = models.DateField(_("closed on"), blank=True, null=True)
    is_open = models.BooleanField(_("open"), default=True)
    is_sent = models.BooleanField(_("sent"), default=False)
    due_on = models.DateField(_("due on"), null=True, blank=True)
    updated_on = models.DateField(_("updated on"), auto_now=True)
    # TODO allways compute total or what?
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comments = models.TextField(_("comments"), blank=True)
    html = models.TextField(_("HTML"), blank=True)
    
    objects = BillManager()
    
    class Meta:
        get_latest_by = 'id'
    
    def __str__(self):
        return self.number
    
    @cached_property
    def seller(self):
        return Account.get_main().billcontact
    
    @cached_property
    def buyer(self):
        return self.account.billcontact
    
    @cached_property
    def payment_state(self):
        if self.is_open or self.get_type() == self.PROFORMA:
            return self.OPEN
        secured = self.transactions.secured().amount()
        if secured >= self.total:
            return self.PAID
        elif self.transactions.exclude_rejected().exists():
            return self.PENDING
        return self.BAD_DEBT
    
    def get_payment_state_display(self):
        value = self.payment_state
        return force_text(dict(self.PAYMENT_STATES).get(value, value))
    
    @classmethod
    def get_class_type(cls):
        return cls.__name__.upper()
    
    def get_type(self):
        return self.type or self.get_class_type()
    
    def set_number(self):
        cls = type(self)
        bill_type = self.get_type()
        if bill_type == self.BILL:
            raise TypeError('This method can not be used on BILL instances')
        prefix = getattr(settings, 'BILLS_%s_NUMBER_PREFIX' % bill_type)
        if self.is_open:
            prefix = 'O{}'.format(prefix)
        bills = cls.objects.filter(number__regex=r'^%s[1-9]+' % prefix)
        last_number = bills.order_by('-number').values_list('number', flat=True).first()
        if last_number is None:
            last_number = 0
        else:
            last_number = int(last_number[len(prefix)+4:])
        number = last_number + 1
        year = timezone.now().strftime("%Y")
        number_length = settings.BILLS_NUMBER_LENGTH
        zeros = (number_length - len(str(number))) * '0'
        number = zeros + str(number)
        self.number = '{prefix}{year}{number}'.format(prefix=prefix, year=year, number=number)
    
    def get_due_date(self, payment=None):
        now = timezone.now()
        if payment:
            return now + payment.get_due_delta()
        return now + relativedelta(months=1)
    
    def close(self, payment=False):
        if not self.is_open:
            raise TypeError("Bill not in Open state.")
        if payment is False:
            payment = self.account.paymentsources.get_default()
        if not self.due_on:
            self.due_on = self.get_due_date(payment=payment)
        self.total = self.get_total()
        self.html = self.render(payment=payment)
        transaction = None
        if self.get_type() != self.PROFORMA:
            transaction = self.transactions.create(bill=self, source=payment, amount=self.total)
        self.closed_on = timezone.now()
        self.is_open = False
        self.is_sent = False
        self.save()
        return transaction
    
    def send(self):
        html = self.html or self.render()
        self.account.send_email(
            template=settings.BILLS_EMAIL_NOTIFICATION_TEMPLATE,
            context={
                'bill': self,
            },
            contacts=(Contact.BILLING,),
            attachments=[
                ('%s.pdf' % self.number, html_to_pdf(html), 'application/pdf')
            ]
        )
        self.is_sent = True
        self.save(update_fields=['is_sent'])
    
    def render(self, payment=False, language=None):
        if payment is False:
            payment = self.account.paymentsources.get_default()
        context = Context({
            'bill': self,
            'lines': self.lines.all().prefetch_related('sublines'),
            'seller': self.seller,
            'buyer': self.buyer,
            'seller_info': {
                'phone': settings.BILLS_SELLER_PHONE,
                'website': settings.BILLS_SELLER_WEBSITE,
                'email': settings.BILLS_SELLER_EMAIL,
                'bank_account': settings.BILLS_SELLER_BANK_ACCOUNT,
            },
            'currency': settings.BILLS_CURRENCY,
            'payment': payment and payment.get_bill_context(),
            'default_due_date': self.get_due_date(payment=payment),
            'now': timezone.now(),
        })
        template_name = 'BILLS_%s_TEMPLATE' % self.get_type()
        template = getattr(settings, template_name, settings.BILLS_DEFAULT_TEMPLATE)
        bill_template = loader.get_template(template)
        with translation.override(language or self.account.language):
            html = bill_template.render(context)
        html = html.replace('-pageskip-', '<pdf:nextpage />')
        return html
    
    def save(self, *args, **kwargs):
        if not self.type:
            self.type = self.get_type()
        if not self.number or (self.number.startswith('O') and not self.is_open):
            self.set_number()
        super(Bill, self).save(*args, **kwargs)
    
    def get_subtotals(self):
        subtotals = {}
        lines = self.lines.annotate(totals=(F('subtotal') + Coalesce(F('sublines__total'), 0)))
        for tax, total in lines.values_list('tax', 'totals'):
            subtotal, taxes = subtotals.get(tax, (0, 0))
            subtotal += total
            subtotals[tax] = (subtotal, round(tax/100*subtotal, 2))
        return subtotals
    
    def get_total(self):
        totals = self.lines.annotate(
            totals=(F('subtotal') + Coalesce(F('sublines__total'), 0)) * (1+F('tax')/100))
        return round(totals.aggregate(Sum('totals'))['totals__sum'], 2)


class Invoice(Bill):
    class Meta:
        proxy = True


class AmendmentInvoice(Bill):
    class Meta:
        proxy = True


class Fee(Bill):
    class Meta:
        proxy = True


class AmendmentFee(Bill):
    class Meta:
        proxy = True


class ProForma(Bill):
    class Meta:
        proxy = True


class BillLine(models.Model):
    """ Base model for bill item representation """
    bill = models.ForeignKey(Bill, verbose_name=_("bill"), related_name='lines')
    description = models.CharField(_("description"), max_length=256)
    rate = models.DecimalField(_("rate"), blank=True, null=True, max_digits=12, decimal_places=2)
    quantity = models.DecimalField(_("quantity"), max_digits=12, decimal_places=2)
    verbose_quantity = models.CharField(_("Verbose quantity"), max_length=16)
    subtotal = models.DecimalField(_("subtotal"), max_digits=12, decimal_places=2)
    tax = models.DecimalField(_("tax"), max_digits=4, decimal_places=2)
    start_on = models.DateField(_("start"))
    end_on = models.DateField(_("end"), null=True)
    order = models.ForeignKey(settings.BILLS_ORDER_MODEL, null=True, blank=True,
        help_text=_("Informative link back to the order"), on_delete=models.SET_NULL)
    order_billed_on = models.DateField(_("order billed"), null=True, blank=True)
    order_billed_until = models.DateField(_("order billed until"), null=True, blank=True)
    created_on = models.DateField(_("created"), auto_now_add=True)
    # Amendment
    amended_line = models.ForeignKey('self', verbose_name=_("amended line"),
            related_name='amendment_lines', null=True, blank=True)
    
    def __str__(self):
        return "#%i" % self.number
    
    @cached_property
    def number(self):
        lines = type(self).objects.filter(bill=self.bill_id)
        return lines.filter(id__lte=self.id).order_by('id').count()
    
    def get_total(self):
        """ Computes subline discounts """
        if self.pk:
            return self.subtotal + sum(self.sublines.values_list('total', flat=True))
    
    def get_verbose_quantity(self):
        return self.verbose_quantity or self.quantity
    
    def get_verbose_period(self):
        ini = self.start_on.strftime("%b, %Y")
        if not self.end_on:
            return ini
        end = (self.end_on - datetime.timedelta(seconds=1)).strftime("%b, %Y")
        if ini == end:
            return ini
        return _("{ini} to {end}").format(ini=ini, end=end)
    
    def undo(self):
        # TODO warn user that undoing bills with compensations lead to compensation lost
        for attr in ['order_id', 'order_billed_on', 'order_billed_until']:
            if not getattr(self, attr):
                raise ValidationError(_("Not enough information stored for undoing"))
        if self.created_on != self.order.billed_on:
            raise ValidationError(_("Dates don't match"))
        self.order.billed_until = self.order_billed_until
        self.order.billed_on = self.order_billed_on
        self.delete()
    
#    def save(self, *args, **kwargs):
#        super(BillLine, self).save(*args, **kwargs)
#        if self.bill.is_open:
#            self.bill.total = self.bill.get_total()
#            self.bill.save(update_fields=['total'])


class BillSubline(models.Model):
    """ Subline used for describing an item discount """
    VOLUME = 'VOLUME'
    COMPENSATION = 'COMPENSATION'
    OTHER = 'OTHER'
    TYPES = (
        (VOLUME, _("Volume")),
        (COMPENSATION, _("Compensation")),
        (OTHER, _("Other")),
    )
    
    # TODO: order info for undoing
    line = models.ForeignKey(BillLine, verbose_name=_("bill line"), related_name='sublines')
    description = models.CharField(_("description"), max_length=256)
    # TODO rename to subtotal
    total = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(_("type"), max_length=16, choices=TYPES, default=OTHER)
    
#    def save(self, *args, **kwargs):
#        # TODO cost of this shit
#        super(BillSubline, self).save(*args, **kwargs)
#        if self.line.bill.is_open:
#            self.line.bill.total = self.line.bill.get_total()
#            self.line.bill.save(update_fields=['total'])


accounts.register(Bill)
