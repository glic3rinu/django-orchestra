from django import forms


class PluginDataForm(forms.ModelForm):
    data = forms.CharField(widget=forms.HiddenInput, required=False)
    
    def __init__(self, *args, **kwargs):
        super(PluginDataForm, self).__init__(*args, **kwargs)
        # TODO remove it well
        try:
            self.fields[self.plugin_field].widget = forms.HiddenInput()
        except KeyError:
            pass
        instance = kwargs.get('instance')
        if instance:
            for field in self.declared_fields:
                initial = self.fields[field].initial
                self.fields[field].initial = instance.data.get(field, initial)
    
    def clean(self):
        data = {}
        for field in self.declared_fields:
            try:
                data[field] = self.cleaned_data[field]
            except KeyError:
                data[field] = self.data[field]
        self.cleaned_data['data'] = data
