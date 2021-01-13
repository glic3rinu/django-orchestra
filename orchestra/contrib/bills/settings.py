from django_countries import data

from orchestra.contrib.settings import Setting
from orchestra.settings import ORCHESTRA_BASE_DOMAIN


BILLS_NUMBER_LENGTH = Setting('BILLS_NUMBER_LENGTH',
    4
)


BILLS_INVOICE_NUMBER_PREFIX = Setting('BILLS_INVOICE_NUMBER_PREFIX',
    'I'
)


BILLS_AMENDMENT_INVOICE_NUMBER_PREFIX = Setting('BILLS_AMENDMENT_INVOICE_NUMBER_PREFIX',
    'A'
)

BILLS_ABONOINVOICE_NUMBER_PREFIX = Setting('BILLS_ABONOINVOICE_NUMBER_PREFIX',
    'AB'
)

BILLS_FEE_NUMBER_PREFIX = Setting('BILLS_FEE_NUMBER_PREFIX',
    'F'
)

BILLS_AMENDMENT_FEE_NUMBER_PREFIX = Setting('BILLS_AMENDMENT_FEE_NUMBER_PREFIX',
    'B'
)


BILLS_PROFORMA_NUMBER_PREFIX = Setting('BILLS_PROFORMA_NUMBER_PREFIX',
    'P'
)


BILLS_DEFAULT_TEMPLATE = Setting('BILLS_DEFAULT_TEMPLATE',
    'bills/microspective.html'
)


BILLS_FEE_TEMPLATE = Setting('BILLS_FEE_TEMPLATE',
    'bills/microspective-fee.html'
)


BILLS_PROFORMA_TEMPLATE = Setting('BILLS_PROFORMA_TEMPLATE',
    'bills/microspective-proforma.html'
)


BILLS_CURRENCY = Setting('BILLS_CURRENCY',
    'euro'
)


BILLS_SELLER_PHONE = Setting('BILLS_SELLER_PHONE',
    '111-112-11-222'
)


BILLS_SELLER_EMAIL = Setting('BILLS_SELLER_EMAIL',
    'sales@{}'.format(ORCHESTRA_BASE_DOMAIN),
    help_text="Uses ORCHESTRA_BASE_DOMAIN by default.",
)


BILLS_SELLER_WEBSITE = Setting('BILLS_SELLER_WEBSITE',
    'www.{}'.format(ORCHESTRA_BASE_DOMAIN),
    help_text="Uses ORCHESTRA_BASE_DOMAIN by default.",
)


BILLS_SELLER_BANK_ACCOUNT = Setting('BILLS_SELLER_BANK_ACCOUNT',
    '0000 0000 00 00000000 (Orchestra Bank)'
)


BILLS_EMAIL_NOTIFICATION_TEMPLATE = Setting('BILLS_EMAIL_NOTIFICATION_TEMPLATE',
    'bills/bill-notification.email'
)


BILLS_ORDER_MODEL = Setting('BILLS_ORDER_MODEL',
    'orders.Order',
    validators=[Setting.validate_model_label]
)


BILLS_CONTACT_DEFAULT_CITY = Setting('BILLS_CONTACT_DEFAULT_CITY',
    'Barcelona'
)


BILLS_CONTACT_COUNTRIES = Setting('BILLS_CONTACT_COUNTRIES',
    tuple((k,v) for k,v in data.COUNTRIES.items()),
    serializable=False
)


BILLS_CONTACT_DEFAULT_COUNTRY = Setting('BILLS_CONTACT_DEFAULT_COUNTRY',
    'ES',
    choices=BILLS_CONTACT_COUNTRIES
)
