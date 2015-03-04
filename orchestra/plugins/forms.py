from django import forms

from orchestra.forms.widgets import ReadOnlyWidget


class PluginDataForm(forms.ModelForm):
    data = forms.CharField(widget=forms.HiddenInput, required=False)
    
    def __init__(self, *args, **kwargs):
        super(PluginDataForm, self).__init__(*args, **kwargs)
        if self.plugin_field in self.fields:
            value = self.plugin.get_name()
            display = '%s <a href=".">change</a>' % unicode(self.plugin.verbose_name)
            self.fields[self.plugin_field].widget = ReadOnlyWidget(value, display)
            self.fields[self.plugin_field].help_text = getattr(self.plugin, 'help_text', '')
        instance = kwargs.get('instance')
        if instance:
            for field in self.declared_fields:
                initial = self.fields[field].initial
                self.fields[field].initial = instance.data.get(field, initial)
            if self.instance.pk:
                for field in self.plugin.get_change_readonly_fileds():
                    value = getattr(self.instance, field, None) or self.instance.data[field]
                    self.fields[field].required = False
                    self.fields[field].widget = ReadOnlyWidget(value)
#                       self.fields[field].help_text = None
    
    def clean(self):
        # TODO clean all filed within data???
        data = {}
        for field in self.declared_fields:
            try:
                data[field] = self.cleaned_data[field]
            except KeyError:
                data[field] = self.data[field]
        self.cleaned_data['data'] = data
