from dateutil import relativedelta
from django import forms

from orchestra.utils import plugins
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from .. import settings


class PaymentMethod(plugins.Plugin):
    label_field = 'label'
    number_field = 'number'
    process_credit = False
    form = None
    serializer = None
    due_delta = relativedelta.relativedelta(months=1)
    
    @classmethod
    @cached
    def get_plugins(cls):
        plugins = []
        for cls in settings.PAYMENTS_ENABLED_METHODS:
            plugins.append(import_class(cls))
        return plugins
    
    @classmethod
    def clean_data(cls, data):
        """ model clean """
        return data
    
    def get_form(self):
        self.form.plugin = self
        self.form.plugin_field = 'method'
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
