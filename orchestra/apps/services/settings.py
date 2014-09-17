from django.conf import settings
from django.utils.translation import ugettext_lazy as _


SERVICES_SERVICE_TAXES = getattr(settings, 'SERVICES_SERVICE_TAXES', (
    (0, _("Duty free")),
    (7, _("7%")),
    (21, _("21%")),
))

SERVICES_SERVICE_DEFAUL_TAX = getattr(settings, 'ORDERS_SERVICE_DFAULT_TAX', 0)


SERVICES_SERVICE_ANUAL_BILLING_MONTH = getattr(settings, 'SERVICES_SERVICE_ANUAL_BILLING_MONTH', 4)
