from django.conf import settings


PAYMENT_CURRENCY = getattr(settings, 'PAYMENT_CURRENCY',
    'Eur'
)


PAYMENTS_DD_CREDITOR_NAME = getattr(settings, 'PAYMENTS_DD_CREDITOR_NAME',
    'Orchestra')


PAYMENTS_DD_CREDITOR_IBAN = getattr(settings, 'PAYMENTS_DD_CREDITOR_IBAN',
    'IE98BOFI90393912121212')


PAYMENTS_DD_CREDITOR_BIC = getattr(settings, 'PAYMENTS_DD_CREDITOR_BIC',
    'BOFIIE2D')


PAYMENTS_DD_CREDITOR_AT02_ID = getattr(settings, 'PAYMENTS_DD_CREDITOR_AT02_ID',
    'InvalidAT02ID')


PAYMENTS_ENABLED_METHODS = getattr(settings, 'PAYMENTS_ENABLED_METHODS', [
    'orchestra.contrib.payments.methods.sepadirectdebit.SEPADirectDebit',
    'orchestra.contrib.payments.methods.creditcard.CreditCard',
])
