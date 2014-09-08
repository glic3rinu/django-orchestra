from django import forms
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import admin_link
from orchestra.forms.widgets import ShowTextWidget


class SelectSourceForm(forms.ModelForm):
    bill_link = forms.CharField(label=_("Number"), required=False,
            widget=ShowTextWidget())
    account_link = forms.CharField(label=_("Account"), required=False)
    display_total = forms.CharField(label=_("Total"), required=False)
    display_type = forms.CharField(label=_("Type"), required=False,
            widget=ShowTextWidget())
    source = forms.ChoiceField(label=_("Source"), required=False)
    
    class Meta:
        fields = (
            'bill_link', 'display_type', 'account_link', 'display_total',
            'source'
        )
        readonly_fields = ('account_link', 'display_total')
    
    def __init__(self, *args, **kwargs):
        super(SelectSourceForm, self).__init__(*args, **kwargs)
        bill = kwargs.get('instance')
        if bill:
            sources = bill.account.paymentsources.filter(is_active=True)
            recharge = bool(bill.total < 0)
            choices = [(None, '-----------')]
            for source in sources:
                if not recharge or source.method_class().allow_recharge:
                    choices.append((source.pk, str(source)))
            self.fields['source'].choices = choices
            self.fields['source'].initial = choices[-1][0]
            self.fields['bill_link'].initial = admin_link('__unicode__')(bill)
            self.fields['display_type'].initial = bill.get_type_display()
    
    def clean_source(self):
        source_id = self.cleaned_data['source']
        if not source_id:
            return None
        source_model = self.instance.account.paymentsources.model
        return source_model.objects.get(id=source_id)
    
    def has_changed(self):
        return False
    
    def save(self, commit=True):
        pass
