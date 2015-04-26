from django.utils.translation import ugettext_lazy as _

from orchestra.settings import Setting


SERVICES_SERVICE_TAXES = Setting('SERVICES_SERVICE_TAXES', (
    (0, _("Duty free")),
    (21, "21%"),
))


SERVICES_SERVICE_DEFAULT_TAX = Setting('SERVICES_SERVICE_DEFAULT_TAX', 0,
    choices=SERVICES_SERVICE_TAXES
)


SERVICES_SERVICE_ANUAL_BILLING_MONTH = Setting('SERVICES_SERVICE_ANUAL_BILLING_MONTH', 1,
    choices=tuple((n, n) for n in range(1, 13))
)


SERVICES_ORDER_MODEL = Setting('SERVICES_ORDER_MODEL',
    'orders.Order'
)


SERVICES_RATE_CLASS = Setting('SERVICES_RATE_CLASS',
    'orchestra.contrib.plans.models.Rate'
)


SERVICES_DEFAULT_IGNORE_PERIOD = Setting('SERVICES_DEFAULT_IGNORE_PERIOD',
    'TEN_DAYS'
)


SERVICES_IGNORE_ACCOUNT_TYPE = Setting('SERVICES_IGNORE_ACCOUNT_TYPE', (
    'superuser',
    'STAFF',
    'FRIEND',
))
