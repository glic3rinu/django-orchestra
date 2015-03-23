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
    due_delta = relativedelta.relativedelta(months=1)
    plugin_field = 'method'
    
    @classmethod
    @cached
    def get_plugins(cls):
        plugins = []
        for cls in settings.PAYMENTS_ENABLED_METHODS:
            plugins.append(import_class(cls))
        return plugins
    
    def get_label(self):
        return self.instance.data[self.label_field]
    
    def get_number(self):
        return self.instance.data[self.number_field]
    
    def get_bill_message(self):
        return ''
