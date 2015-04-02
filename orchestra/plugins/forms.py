from django import forms
from django.utils.encoding import force_text

from orchestra.forms.widgets import ReadOnlyWidget


class PluginDataForm(forms.ModelForm):
    data = forms.CharField(widget=forms.HiddenInput, required=False)
    
    def __init__(self, *args, **kwargs):
        super(PluginDataForm, self).__init__(*args, **kwargs)
        if self.plugin_field in self.fields:
            value = self.plugin.get_name()
            display = '%s <a href=".">change</a>' % force_text(self.plugin.verbose_name)
            self.fields[self.plugin_field].widget = ReadOnlyWidget(value, display)
            self.fields[self.plugin_field].help_text = getattr(self.plugin, 'help_text', '')
        if self.instance:
            for field in self.declared_fields:
                initial = self.fields[field].initial
                self.fields[field].initial = self.instance.data.get(field, initial)
            if self.instance.pk:
                for field in self.plugin.get_change_readonly_fileds():
                    value = getattr(self.instance, field, None) or self.instance.data[field]
                    display = value
                    foo_display = getattr(self.instance, 'get_%s_display' % field, None)
                    if foo_display:
                        display = foo_display()
                    self.fields[field].required = False
                    self.fields[field].widget = ReadOnlyWidget(value, display)
    
    def clean(self):
        data = {}
        # Update data fields
        for field in self.declared_fields:
            try:
                data[field] = self.cleaned_data[field]
            except KeyError:
                data[field] = self.data[field]
        # Keep old data fields
        for field, value in self.instance.data.items():
            if field not in data:
                try:
                    data[field] = self.cleaned_data[field]
                except KeyError:
                    data[field] = value
        self.cleaned_data['data'] = data
