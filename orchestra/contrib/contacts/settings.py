from django_countries import data

from orchestra.contrib.settings import Setting


CONTACTS_DEFAULT_EMAIL_USAGES = Setting('CONTACTS_DEFAULT_EMAIL_USAGES',
    default=(
        'SUPPORT',
        'ADMIN',
        'BILLING',
        'TECH',
        'ADDS',
        'EMERGENCY'
    ),
)


CONTACTS_DEFAULT_CITY = Setting('CONTACTS_DEFAULT_CITY',
    default='Barcelona'
)


CONTACTS_COUNTRIES = Setting('CONTACTS_COUNTRIES',
    default=tuple((k,v) for k,v in data.COUNTRIES.items()),
    serializable=False
)


CONTACTS_DEFAULT_COUNTRY = Setting('CONTACTS_DEFAULT_COUNTRY',
    default='ES',
    choices=CONTACTS_COUNTRIES
)
