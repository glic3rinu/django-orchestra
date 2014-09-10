from dateutil import relativedelta
from django import forms

from orchestra.utils import plugins


class PaymentMethod(plugins.Plugin):
    label_field = 'label'
    number_field = 'number'
    process_credit = False
    form = None
    serializer = None
    due_delta = relativedelta.relativedelta(months=1)
    
    __metaclass__ = plugins.PluginMount
    
    def get_form(self):
        self.form.plugin = self
        return self.form
    
    def get_serializer(self):
        self.serializer.plugin = self
        return self.serializer
    
    def get_label(self, data):
        return data[self.label_field]
    
    def get_number(self, data):
        return data[self.number_field]
    
    def get_bill_message(self, source):
        return ''


class PaymentSourceDataForm(forms.ModelForm):
    class Meta:
        exclude = ('data',) # TODO add 'method'
    
    def __init__(self, *args, **kwargs):
        super(PaymentSourceDataForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            for field in self.declared_fields:
                initial = self.fields[field].initial
                self.fields[field].initial = instance.data.get(field, initial)
    
    def save(self, commit=True):
        plugin = self.plugin
        self.instance.method = plugin.get_plugin_name()
        self.instance.data = {
            field: self.cleaned_data[field] for field in self.declared_fields
        }
        return super(PaymentSourceDataForm, self).save(commit=commit)
