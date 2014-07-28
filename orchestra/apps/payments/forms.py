from django import forms
from django.utils.translation import ugettext_lazy as _
from django_iban.forms import IBANFormField


class PaymentSourceDataForm(forms.ModelForm):
    class Meta:
        exclude = ('data', 'method')
    
    def __init__(self, *args, **kwargs):
        super(PaymentSourceDataForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            for field in self.declared_fields:
                initial = self.fields[field].initial
                self.fields[field].initial = instance.data.get(field, initial)
    
    def save(self, commit=True):
        plugin = self.plugin
        self.instance.method = plugin.get_plugin_name()
        self.instance.data = {
            field: self.cleaned_data[field] for field in self.declared_fields
        }
        return super(PaymentSourceDataForm, self).save(commit=commit)


class BankTransferForm(PaymentSourceDataForm):
    iban = IBANFormField(label='IBAN',
            widget=forms.TextInput(attrs={'size': '50'}))
    name = forms.CharField(max_length=128, label=_("Name"),
            widget=forms.TextInput(attrs={'size': '50'}))


class CreditCardForm(PaymentSourceDataForm):
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
