import inspect

from django.db import models
from django.template import loader, Context
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.accounts.models import Account
from orchestra.core import accounts
from orchestra.utils.functional import cached

from . import settings


class BillManager(models.Manager):
    def get_queryset(self):
        queryset = super(BillManager, self).get_queryset()
        if self.model != Bill:
            bill_type = self.model.get_class_type()
            queryset = queryset.filter(type=bill_type)
        return queryset


class Bill(models.Model):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    SEND = 'SEND'
    RETURNED = 'RETURNED'
    PAID = 'PAID'
    BAD_DEBT = 'BAD_DEBT'
    STATUSES = (
        (OPEN, _("Open")),
        (CLOSED, _("Closed")),
        (SEND, _("Sent")),
        (RETURNED, _("Returned")),
        (PAID, _("Paid")),
        (BAD_DEBT, _("Bad debt")),
    )
    
    TYPES = (
        ('INVOICE', _("Invoice")),
        ('AMENDMENTINVOICE', _("Amendment invoice")),
        ('FEE', _("Fee")),
        ('AMENDMENTFEE', _("Amendment Fee")),
        ('BUDGET', _("Budget")),
    )
    
    number = models.CharField(_("number"), max_length=16, unique=True,
            blank=True)
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
             related_name='%(class)s')
    type = models.CharField(_("type"), max_length=16, choices=TYPES)
    status = models.CharField(_("status"), max_length=16, choices=STATUSES,
            default=OPEN)
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    due_on = models.DateTimeField(_("due on"), null=True, blank=True)
    last_modified_on = models.DateTimeField(_("last modified on"), auto_now=True)
    #base = models.DecimalField(max_digits=12, decimal_places=2)
    #tax = models.DecimalField(max_digits=12, decimal_places=2)
    comments = models.TextField(_("comments"), blank=True)
    # TODO rename to HTML-agnostic term like.. RAW ?
    html = models.TextField(_("HTML"), blank=True)
    
    objects = BillManager()
    
    def __unicode__(self):
        return self.number
    
    @cached_property
    def seller(self):
        return Account.get_main().invoicecontact
    
    @cached_property
    def buyer(self):
        return self.account.invoicecontact
    
    @property
    def lines(self):
        return self.billlines
    
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
        # Bill number resets every natural year
        year = timezone.now().strftime("%Y")
        bills = cls.objects.filter(created_on__year=year)
        number_length = settings.BILLS_NUMBER_LENGTH
        prefix = getattr(settings, 'BILLS_%s_NUMBER_PREFIX' % bill_type)
        if self.status == self.OPEN:
            prefix = 'O{}'.format(prefix)
            bills = bills.filter(status=self.OPEN)
            num_bills = bills.order_by('-number').first() or 0
            if num_bills is not 0:
                num_bills = int(num_bills.number[-number_length:])
        else:
            bills = bills.exclude(status=self.OPEN)
            num_bills = bills.count()
        zeros = (number_length - len(str(num_bills))) * '0'
        number = zeros + str(num_bills + 1)
        self.number = '{prefix}{year}{number}'.format(
                prefix=prefix, year=year, number=number)
    
    def close(self):
        self.status = self.CLOSED
        self.html = self.render()
        self.save()
    
    def render(self):
        context = Context({
            'bill': self,
            'lines': self.lines.all(),
            'seller': self.seller,
            'buyer': self.buyer,
            'seller_info': {
                'phone': settings.BILLS_SELLER_PHONE,
                'website': settings.BILLS_SELLER_WEBSITE,
                'email': settings.BILLS_SELLER_EMAIL,
            },
            'currency': settings.BILLS_CURRENCY,
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
        if not self.number or (self.number.startswith('O') and self.status != self.OPEN):
            self.set_number()
        super(Bill, self).save(*args, **kwargs)
    
    @cached
    def get_subtotals(self):
        subtotals = {}
        for line in self.lines.all():
            subtotal, taxes = subtotals.get(line.tax, (0, 0))
            subtotal += line.total
            for subline in line.sublines.all():
                subtotal += subline.total
            subtotals[line.tax] = (subtotal, (line.tax/100)*subtotal)
        return subtotals
    
    @cached
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


class Budget(Bill):
    class Meta:
        proxy = True
    
    @property
    def lines(self):
        return self.budgetlines


class BaseBillLine(models.Model):
    """ Base model for bill item representation """
    bill = models.ForeignKey(Bill, verbose_name=_("bill"),
            related_name='%(class)ss')
    description = models.CharField(_("description"), max_length=256)
    rate = models.DecimalField(_("rate"), blank=True, null=True,
            max_digits=12, decimal_places=2)
    amount = models.DecimalField(_("amount"), max_digits=12, decimal_places=2)
    total = models.DecimalField(_("total"), max_digits=12, decimal_places=2)
    tax = models.PositiveIntegerField(_("tax"))
    
    class Meta:
        abstract = True
    
    def __unicode__(self):
        return "#%i" % self.number
    
    @cached_property
    def number(self):
        lines = type(self).objects.filter(bill=self.bill_id)
        return lines.filter(id__lte=self.id).order_by('id').count()


class BudgetLine(BaseBillLine):
    pass


class BillLine(BaseBillLine):
    order_id = models.PositiveIntegerField(blank=True, null=True)
    order_last_bill_date = models.DateTimeField(null=True)
    order_billed_until = models.DateTimeField(null=True)
    auto = models.BooleanField(default=False)
    amended_line = models.ForeignKey('self', verbose_name=_("amended line"),
            related_name='amendment_lines', null=True, blank=True)


class BillSubline(models.Model):
    """ Subline used for describing an item discount """
    bill_line = models.ForeignKey(BillLine, verbose_name=_("bill line"),
            related_name='sublines')
    description = models.CharField(_("description"), max_length=256)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    # TODO type ? Volume and Compensation


accounts.register(Bill)
