from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from . import settings
from .methods import PaymentMethod


class PaymentSource(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='payment_sources')
    method = models.CharField(_("method"), max_length=32,
            choices=PaymentMethod.get_plugin_choices())
    data = JSONField(_("data"))
    is_active = models.BooleanField(_("is active"), default=True)


class Transaction(models.Model):
    WAITTING_PROCESSING = 'WAITTING_PROCESSING'
    WAITTING_CONFIRMATION = 'WAITTING_CONFIRMATION'
    CONFIRMED = 'CONFIRMED'
    REJECTED = 'REJECTED'
    LOCKED = 'LOCKED'
    DISCARTED = 'DISCARTED'
    STATES = (
        (WAITTING_PROCESSING, _("Waitting processing")),
        (WAITTING_CONFIRMATION, _("Waitting confirmation")),
        (CONFIRMED, _("Confirmed")),
        (REJECTED, _("Rejected")),
        (LOCKED, _("Locked")),
        (DISCARTED, _("Discarted")),
    )
    
    # TODO account fk?
    bill = models.ForeignKey('bills.bill', verbose_name=_("bill"),
            related_name='transactions')
    method = models.CharField(_("payment method"), max_length=32,
            choices=PaymentMethod.get_plugin_choices())
    state = models.CharField(_("state"), max_length=32, choices=STATES,
            default=WAITTING_PROCESSING)
    data = JSONField(_("data"))
    amount = models.DecimalField(_("amount"), max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default=settings.PAYMENT_CURRENCY)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    related = models.ForeignKey('self', null=True, blank=True)
    
    def __unicode__(self):
        return "Transaction {}".format(self.id)
