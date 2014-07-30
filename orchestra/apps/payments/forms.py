from django import forms
from django.utils.translation import ugettext_lazy as _


# TODO this is for the billing phase
class TransactionCreationForm(forms.ModelForm):
#    transaction_link = forms.CharField()
#    account_link = forms.CharField()
#    bill_link = forms.CharField()
    source = forms.ChoiceField(required=False)
#    exclude = forms.BooleanField(required=False)
    
#    class Meta:
#        model = Bill ?
    
    def __init__(self, *args, **kwargs):
        super(SourceSelectionForm, self).__init__(*args, **kwargs)
        bill = kwargs.get('instance')
        if bill:
            sources = bill.account.payment_sources.filter(is_active=True)
            choices = []
            for source in sources:
                if bill.ammount < 0:
                    if source.method_class().allow_recharge:
                        choices.append((source.method, source.method_display()))
                else:
                    choices.append((source.method, source.method_display()))
            self.fields['source'].choices = choices
    
#    def clean(self):
#        cleaned_data = super(SourceSelectionForm, self).clean()
#        method = cleaned_data.get("method")
#        exclude = cleaned_data.get("exclude")
#        if not method and not exclude:
#            raise forms.ValidationError(_("A transaction should be explicitly "
#                    "excluded when no payment source is available."))


class ProcessTransactionForm(forms.ModelForm):
    pass
