from django import forms
from django.utils.translation import ugettext_lazy as _


class SelectPaymentSourceForm(forms.ModelForm):
    source = forms.ChoiceField(label=_("Source"), required=False)
    
    class Meta:
        fields = ('number', 'source')
    
    def __init__(self, *args, **kwargs):
        super(SelectPaymentSourceForm, self).__init__(*args, **kwargs)
        bill = kwargs.get('instance')
        if bill:
            sources = bill.account.paymentsources.filter(is_active=True)
            recharge = bool(bill.get_total() < 0)
            choices = [(None, '-----------')]
            for source in sources:
                if not recharge or source.method_class().allow_recharge:
                    choices.append((source.pk, str(source)))
            self.fields['source'].choices = choices
    
    def clean_source(self):
        source_id = self.cleaned_data['source']
        if not source_id:
            return None
        source_model = self.instance.account.paymentsources.model
        return source_model.objects.get(id=source_id)
    
    def save(self, commit=True):
        if commit:
            source = self.cleaned_data['source']
            self.instance.close(payment=source)
        return self.instance
