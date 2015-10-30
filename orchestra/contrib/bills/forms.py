from django import forms
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import admin_link
from orchestra.forms import SpanWidget


class SelectSourceForm(forms.ModelForm):
    bill_link = forms.CharField(label=_("Number"), required=False, widget=SpanWidget)
    account_link = forms.CharField(label=_("Account"), required=False, widget=SpanWidget)
    show_total = forms.CharField(label=_("Total"), required=False, widget=SpanWidget)
    display_type = forms.CharField(label=_("Type"), required=False, widget=SpanWidget)
    source = forms.ChoiceField(label=_("Source"), required=False)
    
    class Meta:
        fields = (
            'bill_link', 'display_type', 'account_link', 'show_total', 'source'
        )
    
    def __init__(self, *args, **kwargs):
        super(SelectSourceForm, self).__init__(*args, **kwargs)
        bill = kwargs.get('instance')
        if bill:
            total = bill.compute_total()
            sources = bill.account.paymentsources.filter(is_active=True)
            recharge = bool(total < 0)
            choices = [(None, '-----------')]
            for source in sources:
                if not recharge or source.method_class().allow_recharge:
                    choices.append((source.pk, str(source)))
            self.fields['source'].choices = choices
            self.fields['source'].initial = choices[-1][0]
            self.fields['show_total'].widget.display = total
            self.fields['bill_link'].widget.display = admin_link('__str__')(bill)
            self.fields['display_type'].widget.display = bill.get_type_display()
            self.fields['account_link'].widget.display = admin_link('account')(bill)
    
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
