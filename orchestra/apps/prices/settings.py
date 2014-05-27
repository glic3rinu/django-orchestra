from django.conf import settings
from django.utils.translation import ugettext_lazy as _


PRICES_PACKS = getattr(settings, 'PRICES_PACKS', (
    ('basic', _("Basic")),
    ('advanced', _("Advanced")),
))

PRICES_DEFAULT_PACK = getattr(settings, 'PRICES_DEFAULT_PACK', 'basic')


PRICES_TAXES = getattr(settings, 'PRICES_TAXES', (
    (0, _("Duty free")),
    (7, _("7%")),
    (21, _("21%")),
))

PRICES_DEFAUL_TAX = getattr(settings, 'PRICES_DFAULT_TAX', 0)
