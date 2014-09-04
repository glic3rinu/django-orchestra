from django.conf import settings
from django.utils.translation import ugettext_lazy as _


CONTACTS_DEFAULT_EMAIL_USAGES = getattr(settings, 'CONTACTS_DEFAULT_EMAIL_USAGES',
    ('SUPPORT', 'ADMIN', 'BILL', 'TECH', 'ADDS', 'EMERGENCY')
)


CONTACTS_DEFAULT_CITY = getattr(settings, 'CONTACTS_DEFAULT_CITY', 'Barcelona')

CONTACTS_DEFAULT_PROVINCE = getattr(settings, 'CONTACTS_DEFAULT_PROVINCE', 'Barcelona')

CONTACTS_DEFAULT_COUNTRY = getattr(settings, 'CONTACTS_DEFAULT_COUNTRY', 'Spain')
