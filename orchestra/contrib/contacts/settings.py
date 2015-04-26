from django.conf import settings
from django_countries import data

from orchestra.settings import Setting


CONTACTS_DEFAULT_EMAIL_USAGES = Setting('CONTACTS_DEFAULT_EMAIL_USAGES', (
    'SUPPORT',
    'ADMIN',
    'BILLING',
    'TECH',
    'ADDS',
    'EMERGENCY'
))


CONTACTS_DEFAULT_CITY = Setting('CONTACTS_DEFAULT_CITY',
    'Barcelona'
)


CONTACTS_COUNTRIES = Setting('CONTACTS_COUNTRIES', tuple((k,v) for k,v in data.COUNTRIES.items()),
    editable=False)


CONTACTS_DEFAULT_COUNTRY = Setting('CONTACTS_DEFAULT_COUNTRY', 'ES', choices=CONTACTS_COUNTRIES)
