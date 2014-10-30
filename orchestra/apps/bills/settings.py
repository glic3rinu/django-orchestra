from django.conf import settings
from django_countries import data


BILLS_NUMBER_LENGTH = getattr(settings, 'BILLS_NUMBER_LENGTH', 4)


BILLS_INVOICE_NUMBER_PREFIX = getattr(settings, 'BILLS_INVOICE_NUMBER_PREFIX', 'I')


BILLS_AMENDMENT_INVOICE_NUMBER_PREFIX = getattr(settings, 'BILLS_AMENDMENT_INVOICE_NUMBER_PREFIX', 'A')


BILLS_FEE_NUMBER_PREFIX = getattr(settings, 'BILLS_FEE_NUMBER_PREFIX', 'F')


BILLS_AMENDMENT_FEE_NUMBER_PREFIX = getattr(settings, 'BILLS_AMENDMENT_FEE_NUMBER_PREFIX', 'B')


BILLS_PROFORMA_NUMBER_PREFIX = getattr(settings, 'BILLS_PROFORMA_NUMBER_PREFIX', 'P')


BILLS_DEFAULT_TEMPLATE = getattr(settings, 'BILLS_DEFAULT_TEMPLATE',
        'bills/microspective.html')


BILLS_FEE_TEMPLATE = getattr(settings, 'BILLS_FEE_TEMPLATE',
        'bills/microspective-fee.html')


BILLS_PROFORMA_TEMPLATE = getattr(settings, 'BILLS_PROFORMA_TEMPLATE',
        'bills/microspective-proforma.html')


BILLS_CURRENCY = getattr(settings, 'BILLS_CURRENCY', 'euro')


BILLS_SELLER_PHONE = getattr(settings, 'BILLS_SELLER_PHONE', '111-112-11-222')


BILLS_SELLER_EMAIL = getattr(settings, 'BILLS_SELLER_EMAIL', 'sales@orchestra.lan')


BILLS_SELLER_WEBSITE = getattr(settings, 'BILLS_SELLER_WEBSITE', 'www.orchestra.lan')


BILLS_SELLER_BANK_ACCOUNT = getattr(settings, 'BILLS_SELLER_BANK_ACCOUNT',
        '0000 0000 00 00000000 (Orchestra Bank)')


BILLS_EMAIL_NOTIFICATION_TEMPLATE = getattr(settings, 'BILLS_EMAIL_NOTIFICATION_TEMPLATE',
        'bills/bill-notification.email')


BILLS_ORDER_MODEL = getattr(settings, 'BILLS_ORDER_MODEL', 'orders.Order')


BILLS_CONTACT_DEFAULT_CITY = getattr(settings, 'BILLS_CONTACT_DEFAULT_CITY', 'Barcelona')


BILLS_CONTACT_COUNTRIES = getattr(settings, 'BILLS_CONTACT_COUNTRIES', data.COUNTRIES)


BILLS_CONTACT_DEFAULT_COUNTRY = getattr(settings, 'BILLS_CONTACT_DEFAULT_COUNTRY', 'ES')


