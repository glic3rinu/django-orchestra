from django.conf import settings
from django.utils.translation import ugettext_lazy as _



ENTITIES_TYPE_CHOICES = getattr(settings, 'ENTITIES_TYPE_CHOICES', (
    ('INDIVIDUAL', _('Individual')),
    ('COMPANY', _('Company')),
    ('ASSOCIATION', _('Association')),
    ('PUBLIC_BODY', _('Public_body')),
))

ENTITIES_DEFAULT_TYPE = getattr(settings, 'ENTITIES_DEFAULT_TYPE', 'INDIVIDUAL')


ENTITIES_LANGUAGE_CHOICES = getattr(settings, 'ENTITIES_LANGUAGE_CHOICES', (
    ('en', _('English')),
))

ENTITIES_DEFAULT_LANGUAGE = getattr(settings, 'ENTITIES_DEFAULT_LANGUAGE', 'en')


ENTITIES_DEFAULT_CITY = getattr(settings, 'ENTITIES_DEFAULT_CITY', 'Barcelona')

ENTITIES_DEFAULT_PROVINCE = getattr(settings, 'ENTITIES_DEFAULT_PROVINCE', 'Barcelona')

ENTITIES_DEFAULT_COUNTRY = getattr(settings, 'ENTITIES_DEFAULT_COUNTRY', 'Spain')
