from django import forms
from django.utils.translation import ugettext_lazy as _

from orchestra.forms import ReadOnlyFormMixin
from orchestra.forms.widgets import SpanWidget


class ResourceForm(ReadOnlyFormMixin, forms.ModelForm):
    verbose_name = forms.CharField(label=_("Name"), required=False,
        widget=SpanWidget(tag='<b>'))
    allocated = forms.DecimalField(label=_("Allocated"))
    unit = forms.CharField(label=_("Unit"), required=False)
    
    class Meta:
        fields = ('verbose_name', 'used', 'last_update', 'allocated', 'unit')
        readonly_fields = ('verbose_name', 'unit')
    
    def __init__(self, *args, **kwargs):
        self.resource = kwargs.pop('resource', None)
        if self.resource:
            initial = kwargs.get('initial', {})
            initial.update({
                'verbose_name': self.resource.get_verbose_name(),
                'unit': self.resource.unit,
            })
            kwargs['initial'] = initial
        super(ResourceForm, self).__init__(*args, **kwargs)
        if self.resource:
            if self.resource.on_demand:
                self.fields['allocated'].required = False
                self.fields['allocated'].widget = SpanWidget(original=None, display='')
            else:
                self.fields['allocated'].required = True
                self.fields['allocated'].initial = self.resource.default_allocation
                
#    def has_changed(self):
#        """ Make sure resourcedata objects are created for all resources """
#        if not self.instance.pk:
#            return True
#        return super(ResourceForm, self).has_changed()
    
    def save(self, *args, **kwargs):
        self.instance.resource_id = self.resource.pk
        return super(ResourceForm, self).save(*args, **kwargs)
