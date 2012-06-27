from django.conf import settings
from django.utils.translation import ugettext as _

ugettext = lambda s: s

INVOICE_ID_PREFIX = getattr(settings, 'INVOICE_ID_PREFIX', 'F')
AMENDMENTINVOICE_ID_PREFIX = getattr(settings, 'AMENDMENT_INVOICE_ID_PREFIX', 'RF')
FEE_ID_PREFIX = getattr(settings, 'FEE_ID_PREFIX', 'Q')
AMENDMENTFEE_ID_PREFIX = getattr(settings, 'AMENDMENT_FEE_ID_PREFIX', 'RQ')
BUDGET_ID_PREFIX = getattr(settings, 'BUDGET_ID_PREFIX', 'BU')

INVOICE_ID_LENGTH = getattr(settings, 'INVOICE_ID_LENGTH', 4)
AMENDMENTINVOICE_ID_LENGTH = getattr(settings, 'AMENDMENT_INVOICE_ID_LENGTH', 4)
FEE_ID_LENGTH = getattr(settings, 'FEE_ID_LENGTH', 4)
AMENDMENTFEE_ID_LENGTH = getattr(settings, 'AMENDMENT_FEE_ID_LENGTH', 4)
BUDGET_ID_LENGTH = getattr(settings, 'BUDGET_ID_LENGTH', '4')

INVOICE_TEMPLATE = getattr(settings, 'INVOICE_TEMPLATE', './invoice.html')
AMENDMENTINVOICE_TEMPLATE = getattr(settings, 'AMENDMENTINVOICE_TEMPLATE', './invoice.html')
FEE_TEMPLATE = getattr(settings, 'FEE_TEMPLATE', './invoice.html')
AMENDMENTFEE_TEMPLATE = getattr(settings, 'AMENDMENTFEE_TEMPLATE', './invoice.html')
BUDGET_TEMPLATE = getattr(settings, 'BUDGET_TEMPLATE', './invoice.html')

BILLS_DIRECTORY = getattr(settings, 'BILLS_DIRECTORY', '/tmp/')

DUE_DATE_DAYS = getattr(settings, 'DUE_DATE_DAYS', 30)


#Billing options
DEFAULT_FIXED_POINT = getattr(settings, 'DEFAULT_FIXED_POINT', False)
DEFAULT_FORCE_NEXT = getattr(settings, 'DEFAULT_FORCE_NEXT', True)
DEFAULT_CREATE_NEW_OPEN = getattr(settings, 'DEFAULT_CREATE_NEW_OPEN', True)
DEFAULT_EFFECT = getattr(settings, 'DEFAULT_EFFECT', 'B')

IGNORE_DEPENDENCIES = getattr(settings, 'DEFAULT_EFFECT', 'I')
BILL_DEPENDENCIES = getattr(settings, 'DEFAULT_EFFECT', 'B')
PRICING_DEPENDENCIES = getattr(settings, 'DEFAULT_EFFECT', 'P')

DEFAULT_DEPENDENCIES_EFFECT = getattr(settings, 'DEFAULT_EFFECT', BILL_DEPENDENCIES)

FEE_PER_FEE_LINE = getattr(settings, 'FEE_PER_FEE_LINE', True)

# FEES and INVOICES AMENDMENT Behaviour
CREATE_AMENDMENT_FOR_REFOUND = getattr(settings, 'CREATE_AMENDMENT_FOR_REFOUND', 'A')
CREATE_AMENDMENT_FOR_RECHARGE = getattr(settings, 'CREATE_AMENDMENT_FOR_RECHARGE', 'C')
PUT_REFOUND_ON_OPEN_INVOICE = getattr(settings, 'PUT_REFOUND_ON_OPEN_BILL', 'D')
PUT_REFOUND_ON_OPEN_INVOICE_IF_EQ_TAX = getattr(settings, 'PUT_REFOUND_ON_OPEN_BILL_IF_EQ_TAX', 'E')
PUT_RECHARGE_ON_OPEN_INVOICE = getattr(settings, 'PUT_RECHARGE_ON_OPEN_BILL', 'F')
#GROUP_REFOUND_AND_RECHARGE = getattr(settings, 'GROUP_REFOUND_AND_RECHARGE', 'G')

INVOICES_AMENDMENT_BEHAVIOUR = getattr(settings, 'INVOICES_AMENDMENT_BEHAVIOUR', [PUT_RECHARGE_ON_OPEN_INVOICE, 
            CREATE_AMENDMENT_FOR_REFOUND, PUT_REFOUND_ON_OPEN_INVOICE_IF_EQ_TAX])
FEES_AMENDMENT_BEHAVIOUR = getattr(settings, 'FEES_AMENDMENT_BEHAVIOUR', [CREATE_AMENDMENT_FOR_REFOUND, 
            CREATE_AMENDMENT_FOR_RECHARGE])


OPEN = getattr(settings, 'OPEN', 'OPEN')
CLOSED = getattr(settings, 'CLOSED', 'CLOSED')
SEND = getattr(settings, 'SEND', 'SEND')
RETURNED = getattr(settings, 'RETURNED', 'RETURNED')
PAYD = getattr(settings, 'PAYD', 'PAYD')
IRRECOVRABLE = getattr(settings, 'IRRECOVRABLE', 'IRRECOVRABLE')

STATUS_CHOICES = getattr(settings, 'STATUS_CHOICES', ((OPEN, _('Open')),
                                                      (CLOSED, _('Closed')),
                                                      (SEND, _('Sent')),
                                                      (RETURNED, _('Returned')),
                                                      (PAYD, _('Payd')),
                                                      (IRRECOVRABLE, _('Irrecovrable debt')),))
