from django.conf import settings
from django_countries import data


CONTACTS_DEFAULT_EMAIL_USAGES = getattr(settings, 'CONTACTS_DEFAULT_EMAIL_USAGES', (
    'SUPPORT',
    'ADMIN',
    'BILLING',
    'TECH',
    'ADDS',
    'EMERGENCY'
))


CONTACTS_DEFAULT_CITY = getattr(settings, 'CONTACTS_DEFAULT_CITY',
'Barcelona'
)


CONTACTS_COUNTRIES = getattr(settings, 'CONTACTS_COUNTRIES', (
    (k,v) for k,v in data.COUNTRIES.iteritems()
))


CONTACTS_DEFAULT_COUNTRY = getattr(settings, 'CONTACTS_DEFAULT_COUNTRY',
    'ES'
)
