from django.conf import settings
from django.utils.translation import ugettext_lazy as _


PRICES_PACKS = getattr(settings, 'PRICES_PACKS', (
    ('basic', _("Basic")),
    ('advanced', _("Advanced")),
))

PRICES_DEFAULT_PACK = getattr(settings, 'PRICES_DEFAULT_PACK', 'basic')
