from django.conf import settings
from django.utils.translation import ugettext_lazy as _



CONTACTS_TYPE_CHOICES = getattr(settings, 'CONTACTS_TYPE_CHOICES', (
    ('INDIVIDUAL', _('Individual')),
    ('COMPANY', _('Company')),
    ('ASSOCIATION', _('Association')),
    ('PUBLIC_BODY', _('Public_body')),
))

CONTACTS_DEFAULT_TYPE = getattr(settings, 'CONTACTS_DEFAULT_TYPE', 'INDIVIDUAL')


CONTACTS_LANGUAGE_CHOICES = getattr(settings, 'CONTACTS_LANGUAGE_CHOICES', (
    ('en', _('English')),
))

CONTACTS_DEFAULT_LANGUAGE = getattr(settings, 'CONTACTS_DEFAULT_LANGUAGE', 'en')


CONTACTS_DEFAULT_CITY = getattr(settings, 'CONTACTS_DEFAULT_CITY', 'Barcelona')

CONTACTS_DEFAULT_PROVINCE = getattr(settings, 'CONTACTS_DEFAULT_PROVINCE', 'Barcelona')

CONTACTS_DEFAULT_COUNTRY = getattr(settings, 'CONTACTS_DEFAULT_COUNTRY', 'Spain')


CONTACTS_CONTRACT_MODELS = getattr(settings, 'CONTACTS_CONTRACT_MODELS', ())
