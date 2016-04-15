import importlib
import logging
import os
from dateutil import relativedelta
from functools import lru_cache

from orchestra import plugins
from orchestra.utils.python import import_class

from .. import settings


class PaymentMethod(plugins.Plugin, metaclass=plugins.PluginMount):
    label_field = 'label'
    number_field = 'number'
    allow_recharge = False
    due_delta = relativedelta.relativedelta(months=1)
    plugin_field = 'method'
    state_help = {}
    
    @classmethod
    @lru_cache()
    def get_plugins(cls, all=False):
        if all:
            for module in os.listdir(os.path.dirname(__file__)):
                if module not in ('options.py', '__init__.py') and module[-3:] == '.py':
                    importlib.import_module('.'+module[:-3], __package__)
            plugins = super().get_plugins()
        else:
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
