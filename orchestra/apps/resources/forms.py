from django import forms
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from djcelery.humanize import naturaldate

from orchestra.forms.widgets import ShowTextWidget, ReadOnlyWidget


class ResourceForm(forms.ModelForm):
    verbose_name = forms.CharField(label=_("Name"), widget=ShowTextWidget(bold=True),
            required=False)
    used = forms.IntegerField(label=_("Used"), widget=ShowTextWidget(),
            required=False)
    allocated = forms.IntegerField(label=_("Allocated"))
    
    class Meta:
        fields = ('verbose_name', 'used', 'last_update', 'allocated',)
    
    def __init__(self, *args, **kwargs):
        self.resource = kwargs.pop('resource', None)
        super(ResourceForm, self).__init__(*args, **kwargs)
        if self.resource:
            self.fields['verbose_name'].initial = self.resource.verbose_name
            if self.resource.ondemand:
                self.fields['allocated'].required = False
                self.fields['allocated'].widget = ReadOnlyWidget(None, '')
            else:
                self.fields['allocated'].required = True
                self.fields['allocated'].initial = self.resource.default_allocation
    
    def has_changed(self):
        """ Make sure resourcedata objects are created for all resources """
        if not self.instance.pk:
            return True
        return super(ResourceForm, self).has_changed()
    
    def save(self, *args, **kwargs):
        self.instance.resource_id = self.resource.pk
        return super(ResourceForm, self).save(*args, **kwargs)
