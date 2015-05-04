import logging
from dateutil import relativedelta

from orchestra import plugins
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from .. import settings


logger = logging.getLogger(__name__)


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
            try:
                plugins.append(import_class(cls))
            except ImportError as exc:
                logger.error('Error loading %s: %s' % (cls, str(exc)))
        return plugins
    
    def get_label(self):
        return self.instance.data[self.label_field]
    
    def get_number(self):
        return self.instance.data[self.number_field]
    
    def get_bill_message(self):
        return ''
