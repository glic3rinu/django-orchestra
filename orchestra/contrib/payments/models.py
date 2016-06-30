from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from orchestra.models.fields import PrivateFileField
from orchestra.models.queryset import group_by

from . import settings
from .methods import PaymentMethod


class PaymentSourcesQueryset(models.QuerySet):
    def get_default(self):
        return self.filter(is_active=True).first()


class PaymentSource(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
        related_name='paymentsources')
    method = models.CharField(_("method"), max_length=32,
        choices=PaymentMethod.get_choices())
    data = JSONField(_("data"), default={})
    is_active = models.BooleanField(_("active"), default=True)
    
    objects = PaymentSourcesQueryset.as_manager()
    
    def __str__(self):
        return "%s (%s)" % (self.label, self.method_class.verbose_name)
    
    @cached_property
    def method_class(self):
        return PaymentMethod.get(self.method)
    
    @cached_property
    def method_instance(self):
        """ Per request lived method_instance """
        return self.method_class(self)
    
    @cached_property
    def label(self):
        return self.method_instance.get_label()
    
    @cached_property
    def number(self):
        return self.method_instance.get_number()
    
    def get_bill_context(self):
        method = self.method_instance
        return {
            'message': method.get_bill_message(),
        }
    
    def get_due_delta(self):
        return self.method_instance.due_delta
    
    def clean(self):
        self.data = self.method_instance.clean_data()


class TransactionQuerySet(models.QuerySet):
    group_by = group_by
    
    def create(self, **kwargs):
        source = kwargs.get('source')
        if source is None or not hasattr(source.method_class, 'process'):
            # Manual payments don't need processing
            kwargs['state'] = self.model.WAITTING_EXECUTION
        amount = kwargs.get('amount')
        if amount == 0:
            kwargs['state'] = self.model.SECURED
        return super(TransactionQuerySet, self).create(**kwargs)
    
    def secured(self):
        return self.filter(state=Transaction.SECURED)
    
    def exclude_rejected(self):
        return self.exclude(state=Transaction.REJECTED)
    
    def amount(self):
        return next(iter(self.aggregate(models.Sum('amount')).values())) or 0
    
    def processing(self):
        return self.filter(state__in=[Transaction.EXECUTED, Transaction.WAITTING_EXECUTION])


class Transaction(models.Model):
    WAITTING_PROCESSING = 'WAITTING_PROCESSING' # CREATED
    WAITTING_EXECUTION = 'WAITTING_EXECUTION' # PROCESSED
    EXECUTED = 'EXECUTED'
    SECURED = 'SECURED'
    REJECTED = 'REJECTED'
    STATES = (
        (WAITTING_PROCESSING, _("Waitting processing")),
        (WAITTING_EXECUTION, _("Waitting execution")),
        (EXECUTED, _("Executed")),
        (SECURED, _("Secured")),
        (REJECTED, _("Rejected")),
    )
    STATE_HELP = {
        WAITTING_PROCESSING: _("The transaction is created and requires processing by the "
                               "specific payment method."),
        WAITTING_EXECUTION: _("The transaction is processed and its pending execution on "
                              "the related financial institution."),
        EXECUTED: _("The transaction is executed on the financial institution."),
        SECURED: _("The transaction ammount is secured."),
        REJECTED: _("The transaction has failed and the ammount is lost, a new transaction "
                    "should be created for recharging."),
    }
    
    bill = models.ForeignKey('bills.bill', verbose_name=_("bill"),
        related_name='transactions')
    source = models.ForeignKey(PaymentSource, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_("source"), related_name='transactions')
    process = models.ForeignKey('payments.TransactionProcess', null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name=_("process"), related_name='transactions')
    state = models.CharField(_("state"), max_length=32, choices=STATES,
        default=WAITTING_PROCESSING)
    amount = models.DecimalField(_("amount"), max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default=settings.PAYMENT_CURRENCY)
    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    modified_at = models.DateTimeField(_("modified"), auto_now=True)
    
    objects = TransactionQuerySet.as_manager()
    
    def __str__(self):
        return "#%i" % self.id
    
    @property
    def account(self):
        return self.bill.account
    
    def clean(self):
        if not self.pk:
            amount = self.bill.transactions.exclude(state=self.REJECTED).amount()
            if amount >= self.bill.total:
                raise ValidationError(
                    _("Bill %(number)s already has valid transactions that cover bill total amount (%(amount)s).") % {
                        'number': self.bill.number,
                        'amount': amount,
                    }
                )
    
    def get_state_help(self):
        if self.source:
            return self.source.method_instance.state_help.get(self.state) or self.STATE_HELP.get(self.state)
        return self.STATE_HELP.get(self.state)
    
    def mark_as_processed(self):
        self.state = self.WAITTING_EXECUTION
        self.save(update_fields=('state', 'modified_at'))
    
    def mark_as_executed(self):
        self.state = self.EXECUTED
        self.save(update_fields=('state', 'modified_at'))
    
    def mark_as_secured(self):
        self.state = self.SECURED
        self.save(update_fields=('state', 'modified_at'))
    
    def mark_as_rejected(self):
        self.state = self.REJECTED
        self.save(update_fields=('state', 'modified_at'))


class TransactionProcess(models.Model):
    """
    Stores arbitrary data generated by payment methods while processing transactions
    """
    CREATED = 'CREATED'
    EXECUTED = 'EXECUTED'
    ABORTED = 'ABORTED'
    COMMITED = 'COMMITED'
    STATES = (
        (CREATED, _("Created")),
        (EXECUTED, _("Executed")),
        (ABORTED, _("Aborted")),
        (COMMITED, _("Commited")),
    )
    
    data = JSONField(_("data"), blank=True)
    file = PrivateFileField(_("file"), blank=True)
    state = models.CharField(_("state"), max_length=16, choices=STATES, default=CREATED)
    created_at = models.DateTimeField(_("created"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("updated"), auto_now=True)
    
    class Meta:
        verbose_name_plural = _("Transaction processes")
    
    def __str__(self):
        return '#%i' % self.id
    
    def mark_as_executed(self):
        self.state = self.EXECUTED
        for transaction in self.transactions.all():
            transaction.mark_as_executed()
        self.save(update_fields=('state', 'updated_at'))
    
    def abort(self):
        self.state = self.ABORTED
        for transaction in self.transactions.all():
            transaction.mark_as_rejected()
        self.save(update_fields=('state', 'updated_at'))
    
    def commit(self):
        self.state = self.COMMITED
        for transaction in self.transactions.processing():
            transaction.mark_as_secured()
        self.save(update_fields=('state', 'updated_at'))
