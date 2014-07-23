from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from . import settings


class BillManager(models.Manager):
    def get_queryset(self):
        queryset = super(BillManager, self).get_queryset()
        if self.model != Bill:
            bill_type = self.model.get_type()
            queryset = queryset.filter(bill_type=bill_type)
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
    
    ident = models.CharField(_("identifier"), max_length=16, unique=True,
            blank=True)
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
             related_name='%(class)s')
    bill_type = models.CharField(_("type"), max_length=16, choices=TYPES)
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
        return self.ident
    
    @classmethod
    def get_type(cls):
        return cls.__name__.upper()
    
    def set_ident(self):
        cls = type(self)
        bill_type = self.bill_type or cls.get_type()
        if bill_type == 'BILL':
            raise TypeError("get_new_ident() can not be used on a Bill class")
        # Bill number resets every natural year
        year = timezone.now().strftime("%Y")
        bills = cls.objects.filter(created_on__year=year)
        number_length = settings.BILLS_IDENT_NUMBER_LENGTH
        prefix = getattr(settings, 'BILLS_%s_IDENT_PREFIX' % bill_type)
        if self.status == self.OPEN:
            prefix = 'O{}'.format(prefix)
            bills = bills.filter(status=self.OPEN)
            num_bills = bills.order_by('-ident').first() or 0
            if num_bills is not 0:
                num_bills = int(num_bills.ident[-number_length:])
        else:
            bills = bills.exclude(status=self.OPEN)
            num_bills = bills.count()
        zeros = (number_length - len(str(num_bills))) * '0'
        number = zeros + str(num_bills + 1)
        self.ident = '{prefix}{year}{number}'.format(
                prefix=prefix, year=year, number=number)
    
    def save(self, *args, **kwargs):
        if not self.bill_type:
            self.bill_type = type(self).get_type()
        if not self.ident or (self.ident.startswith('O') and self.status != self.OPEN):
            self.set_ident()
        super(Bill, self).save(*args, **kwargs)


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


class BaseBillLine(models.Model):
    bill = models.ForeignKey(Bill, verbose_name=_("bill"),
            related_name='%(class)ss')
    description = models.CharField(max_length=256)
    initial_date = models.DateTimeField()
    final_date = models.DateTimeField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.IntegerField()
    tax = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        abstract = True


class BudgetLine(BaseBillLine):
    pass


class BillLine(BaseBillLine):
    order_id = models.PositiveIntegerField(blank=True)
    order_last_bill_date = models.DateTimeField(null=True)
    order_billed_until = models.DateTimeField(null=True)
    auto = models.BooleanField(default=False)
    amended_line = models.ForeignKey('self', verbose_name=_("amended line"),
            related_name='amendment_lines', null=True, blank=True)

