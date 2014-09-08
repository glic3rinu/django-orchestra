from django.conf import settings
from django.utils.translation import ugettext_lazy as _


ORDERS_SERVICE_TAXES = getattr(settings, 'ORDERS_SERVICE_TAXES', (
    (0, _("Duty free")),
    (7, _("7%")),
    (21, _("21%")),
))

ORDERS_SERVICE_DEFAUL_TAX = getattr(settings, 'ORDERS_SERVICE_DFAULT_TAX', 0)


ORDERS_SERVICE_ANUAL_BILLING_MONTH = getattr(settings, 'ORDERS_SERVICE_ANUAL_BILLING_MONTH', 4)


ORDERS_BILLING_BACKEND = getattr(settings, 'ORDERS_BILLING_BACKEND',
        'orchestra.apps.orders.billing.BillsBackend')


ORDERS_PLANS = getattr(settings, 'ORDERS_PLANS', (
    ('basic', _("Basic")),
    ('advanced', _("Advanced")),
))

ORDERS_DEFAULT_PLAN = getattr(settings, 'ORDERS_DEFAULT_PLAN', 'basic')
