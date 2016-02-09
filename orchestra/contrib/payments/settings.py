from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.settings import Setting

from .. import payments


PAYMENT_CURRENCY = Setting('PAYMENT_CURRENCY',
    'Eur'
)


PAYMENTS_DD_BILL_MESSAGE = Setting('PAYMENTS_DD_BILL_MESSAGE',
    _("<strong>Direct debit</strong>, this bill will be automatically charged "
      "to your bank account with IBAN number<br><strong>%(number)s</strong>."),
)

PAYMENTS_DD_CREDITOR_NAME = Setting('PAYMENTS_DD_CREDITOR_NAME',
    'Orchestra'
)


PAYMENTS_DD_CREDITOR_IBAN = Setting('PAYMENTS_DD_CREDITOR_IBAN',
    'IE98BOFI90393912121212'
)


PAYMENTS_DD_CREDITOR_BIC = Setting('PAYMENTS_DD_CREDITOR_BIC',
    'BOFIIE2D'
)


PAYMENTS_DD_CREDITOR_AT02_ID = Setting('PAYMENTS_DD_CREDITOR_AT02_ID',
    'InvalidAT02ID'
)


PAYMENTS_ENABLED_METHODS = Setting('PAYMENTS_ENABLED_METHODS',
    (
        'orchestra.contrib.payments.methods.sepadirectdebit.SEPADirectDebit',
        'orchestra.contrib.payments.methods.creditcard.CreditCard',
    ),
    # lazy loading
    choices=lambda : ((m.get_class_path(), m.get_class_path()) for m in payments.methods.PaymentMethod.get_plugins(all=True)),
    multiple=True,
)
