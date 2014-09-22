import inspect
from dateutil.relativedelta import relativedelta

from django.db import models
from django.template import loader, Context
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.accounts.models import Account
from orchestra.core import accounts
from orchestra.utils.functional import cached
from orchestra.utils.html import html_to_pdf

from . import settings


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
    
    TYPES = (
        ('INVOICE', _("Invoice")),
        ('AMENDMENTINVOICE', _("Amendment invoice")),
        ('FEE', _("Fee")),
        ('AMENDMENTFEE', _("Amendment Fee")),
        ('PROFORMA', _("Pro forma")),
    )
    
    number = models.CharField(_("number"), max_length=16, unique=True,
            blank=True)
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
             related_name='%(class)s')
    type = models.CharField(_("type"), max_length=16, choices=TYPES)
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    closed_on = models.DateTimeField(_("closed on"), blank=True, null=True)
    # TODO rename to is_closed
    is_open = models.BooleanField(_("is open"), default=True)
    is_sent = models.BooleanField(_("is sent"), default=False)
    due_on = models.DateField(_("due on"), null=True, blank=True)
    last_modified_on = models.DateTimeField(_("last modified on"), auto_now=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comments = models.TextField(_("comments"), blank=True)
    html = models.TextField(_("HTML"), blank=True)
    
    objects = BillManager()
    
    class Meta:
        get_latest_by = 'created_on'
    
    def __unicode__(self):
        return self.number
    
    @cached_property
    def seller(self):
        return Account.get_main().invoicecontact
    
    @cached_property
    def buyer(self):
        return self.account.invoicecontact
    
    @cached_property
    def payment_state(self):
        if self.is_open:
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
        if bill_type == 'BILL':
            raise TypeError("get_new_number() can not be used on a Bill class")
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
        self.number = '{prefix}{year}{number}'.format(
                prefix=prefix, year=year, number=number)
    
    def get_due_date(self, payment=None):
        now = timezone.now()
        if payment:
            return now + payment.get_due_delta()
        return now + relativedelta(months=1)
    
    def close(self, payment=False):
        assert self.is_open, "Bill not in Open state"
        if payment is False:
            payment = self.account.paymentsources.get_default()
        if not self.due_on:
            self.due_on = self.get_due_date(payment=payment)
        self.total = self.get_total()
        self.html = self.render(payment=payment)
        if self.get_type() != 'PROFORMA':
            self.transactions.create(bill=self, source=payment, amount=self.total)
        self.closed_on = timezone.now()
        self.is_open = False
        self.is_sent = False
        self.save()
    
    def send(self):
        from orchestra.apps.contacts.models import Contact
        self.account.send_email(
            template=settings.BILLS_EMAIL_NOTIFICATION_TEMPLATE,
            context={
                'bill': self,
            },
            contacts=(Contact.BILLING,),
            attachments=[
                ('%s.pdf' % self.number, html_to_pdf(self.html), 'application/pdf')
            ]
        )
        self.is_sent = True
        self.save()
    
    def render(self, payment=False):
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
        template = getattr(settings, 'BILLS_%s_TEMPLATE' % self.get_type(),
                settings.BILLS_DEFAULT_TEMPLATE)
        bill_template = loader.get_template(template)
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
        for line in self.lines.all():
            subtotal, taxes = subtotals.get(line.tax, (0, 0))
            subtotal += line.get_total()
            subtotals[line.tax] = (subtotal, (line.tax/100)*subtotal)
        return subtotals
    
    def get_total(self):
        total = 0
        for tax, subtotal in self.get_subtotals().iteritems():
            subtotal, taxes = subtotal
            total += subtotal + taxes
        return total


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
    rate = models.DecimalField(_("rate"), blank=True, null=True,
            max_digits=12, decimal_places=2)
    quantity = models.DecimalField(_("quantity"), max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(_("subtotal"), max_digits=12, decimal_places=2)
    tax = models.PositiveIntegerField(_("tax"))
    # TODO
#    order_id = models.ForeignKey('orders.Order', null=True, blank=True,
#            help_text=_("Informative link back to the order"))
    amended_line = models.ForeignKey('self', verbose_name=_("amended line"),
            related_name='amendment_lines', null=True, blank=True)
    
    def __unicode__(self):
        return "#%i" % self.number
    
    @cached_property
    def number(self):
        lines = type(self).objects.filter(bill=self.bill_id)
        return lines.filter(id__lte=self.id).order_by('id').count()
    
    def get_total(self):
        """ Computes subline discounts """
        total = self.subtotal
        for subline in self.sublines.all():
            total += subline.total
        return total
    
    def save(self, *args, **kwargs):
        # TODO cost of this shit
        super(BillLine, self).save(*args, **kwargs)
        if self.bill.is_open:
            self.bill.total = self.bill.get_total()
            self.bill.save()


class BillSubline(models.Model):
    """ Subline used for describing an item discount """
    line = models.ForeignKey(BillLine, verbose_name=_("bill line"),
            related_name='sublines')
    description = models.CharField(_("description"), max_length=256)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    # TODO type ? Volume and Compensation
    
    def save(self, *args, **kwargs):
        # TODO cost of this shit
        super(BillSubline, self).save(*args, **kwargs)
        if self.line.bill.is_open:
            self.line.bill.total = self.line.bill.get_total()
            self.line.bill.save()


accounts.register(Bill)
