from django import forms
from django.utils.translation import ugettext_lazy as _

from orchestra.forms.widgets import ShowTextWidget, ReadOnlyWidget


class ResourceForm(forms.ModelForm):
    verbose_name = forms.CharField(label=_("Name"), widget=ShowTextWidget(bold=True),
            required=False)
    current = forms.CharField(label=_("Current"), widget=ShowTextWidget(),
            required=False)
    value = forms.CharField(label=_("Allocation"))
    
    class Meta:
        fields = ('verbose_name', 'current', 'value',)
    
    def __init__(self, *args, **kwargs):
        self.resource = kwargs.pop('resource', None)
        super(ResourceForm, self).__init__(*args, **kwargs)
        if self.resource:
            self.fields['verbose_name'].initial = self.resource.verbose_name
            self.fields['current'].initial = self.resource.get_current()
            if self.resource.ondemand:
                self.fields['value'].widget = ReadOnlyWidget('')
            else:
                self.fields['value'].initial = self.resource.default_allocation
    
    def save(self, *args, **kwargs):
        self.instance.resource_id = self.resource.pk
        return super(ResourceForm, self).save(*args, **kwargs)
