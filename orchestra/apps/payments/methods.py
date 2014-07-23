from django.utils.translation import ugettext_lazy as _

from orchestra.utils import plugins


class PaymentMethod(plugins.Plugin):
    __metaclass__ = plugins.PluginMount


class BankTransfer(PaymentMethod):
    verbose_name = _("Bank transfer")


class CreditCard(PaymentMethod):
    verbose_name = _("Credit card")
