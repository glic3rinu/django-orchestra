from dateutil import relativedelta
from django import forms
from django.core.exceptions import ValidationError

from orchestra import plugins
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
        """ model clean, uses cls.serializer by default """
        serializer = cls.serializer(data=data)
        if not serializer.is_valid():
            serializer.errors.pop('non_field_errors', None)
            raise ValidationError(serializer.errors)
        return serializer.data
    
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
