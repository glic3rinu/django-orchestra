from django import forms
from django.utils.encoding import force_text

from orchestra.forms.widgets import SpanWidget


class PluginDataForm(forms.ModelForm):
    data = forms.CharField(widget=forms.HiddenInput, required=False)
    
    def __init__(self, *args, **kwargs):
        super(PluginDataForm, self).__init__(*args, **kwargs)
        if self.plugin_field in self.fields:
            value = self.plugin.get_name()
            display = '%s <a href=".">change</a>' % force_text(self.plugin.verbose_name)
            self.fields[self.plugin_field].widget = SpanWidget(original=value, display=display)
            help_text = self.fields[self.plugin_field].help_text
            self.fields[self.plugin_field].help_text = getattr(self.plugin, 'help_text', help_text)
        if self.instance:
            for field in self.declared_fields:
                initial = self.fields[field].initial
                self.fields[field].initial = self.instance.data.get(field, initial)
            if self.instance.pk:
                # Admin Readonly fields are not availeble in self.fields, so we use Meta
                plugin = getattr(self.instance, '%s_class' % self.plugin_field)
                plugin_help_text = getattr(plugin, 'help_text', '')
                model_help_text = self.instance._meta.get_field_by_name(self.plugin_field)[0].help_text
                self._meta.help_texts = {
                    self.plugin_field: plugin_help_text or model_help_text
                }
                for field in self.plugin.get_change_readonly_fileds():
                    value = getattr(self.instance, field, None) or self.instance.data.get(field)
                    display = value
                    foo_display = getattr(self.instance, 'get_%s_display' % field, None)
                    if foo_display:
                        display = foo_display()
                    self.fields[field].required = False
                    self.fields[field].widget = SpanWidget(original=value, display=display)
    
    def clean(self):
        super(PluginDataForm, self).clean()
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
