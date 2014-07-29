from django.conf import settings


PAYMENT_CURRENCY = getattr(settings, 'PAYMENT_CURRENCY', 'Eur')


PAYMENTS_DD_CREDITOR_NAME = getattr(settings, 'PAYMENTS_DD_CREDITOR_NAME',
    'Orchestra')
PAYMENTS_DD_CREDITOR_IBAN = getattr(settings, 'PAYMENTS_DD_CREDITOR_IBAN',
    'InvalidIBAN')
PAYMENTS_DD_CREDITOR_BIC = getattr(settings, 'PAYMENTS_DD_CREDITOR_BIC',
    'InvalidBIC')
PAYMENTS_DD_CREDITOR_AT02_ID = getattr(settings, 'PAYMENTS_DD_CREDITOR_AT02_ID',
    'InvalidAT02ID')
