from django import forms


class PluginDataForm(forms.ModelForm):
    class Meta:
        exclude = ('data',)
    
    def __init__(self, *args, **kwargs):
        super(PluginDataForm, self).__init__(*args, **kwargs)
        # TODO remove it weel
        try:
            self.fields[self.plugin_field].widget = forms.HiddenInput()
        except KeyError:
            pass
        instance = kwargs.get('instance')
        if instance:
            for field in self.declared_fields:
                initial = self.fields[field].initial
                self.fields[field].initial = instance.data.get(field, initial)
    
    def save(self, commit=True):
        plugin = self.plugin
        setattr(self.instance, self.plugin_field, plugin.get_plugin_name())
        self.instance.data = {
            field: self.cleaned_data[field] for field in self.declared_fields
        }
        return super(PluginDataForm, self).save(commit=commit)
