from django.utils.translation import ugettext_lazy as _
from django_iban.validators import IBANValidator, IBAN_COUNTRY_CODE_LENGTH
from rest_framework import serializers

from orchestra.utils import plugins

from .forms import BankTransferForm, CreditCardForm


class PaymentMethod(plugins.Plugin):
    label_field = 'label'
    number_field = 'number'
    
    __metaclass__ = plugins.PluginMount
    
    def get_form(self):
        self.form.plugin = self
        return self.form
    
    def get_serializer(self):
        self.serializer.plugin = self
        return self.serializer
    
    def get_label(self, data):
        return data[self.label_field]
    
    def get_number(self, data):
        return data[self.number_field]


class BankTransferSerializer(serializers.Serializer):
    iban = serializers.CharField(label='IBAN', validators=[IBANValidator()],
            min_length=min(IBAN_COUNTRY_CODE_LENGTH.values()), max_length=34)
    name = serializers.CharField(label=_("Name"), max_length=128)


class CreditCardSerializer(serializers.Serializer):
    pass


class BankTransfer(PaymentMethod):
    verbose_name = _("Bank transfer")
    label_field = 'name'
    number_field = 'iban'
    form = BankTransferForm
    serializer = BankTransferSerializer


class CreditCard(PaymentMethod):
    verbose_name = _("Credit card")
    form = CreditCardForm
    serializer = CreditCardSerializer
