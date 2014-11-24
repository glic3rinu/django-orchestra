from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.plugins.forms import PluginDataForm

from .options import PaymentMethod


class CreditCardForm(PluginDataForm):
    label = forms.CharField(max_length=128, label=_("Label"),
            help_text=_("Use a name such as \"Jo's Visa\" to remember which "
                        "card it is."))
    first_name = forms.CharField(max_length=128)
    last_name = forms.CharField(max_length=128)
    address = forms.CharField(max_length=128)
    zip = forms.CharField(max_length=128)
    city = forms.CharField(max_length=128)
    country = forms.CharField(max_length=128)
    card_number = forms.CharField(max_length=128)
    expiration_date = forms.CharField(max_length=128)
    security_code = forms.CharField(max_length=128)


class CreditCardSerializer(serializers.Serializer):
    pass


class CreditCard(PaymentMethod):
    verbose_name = _("Credit card")
    form = CreditCardForm
    serializer = CreditCardSerializer
