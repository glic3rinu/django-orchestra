from django.conf import settings
from django.utils.translation import ugettext as _

ugettext = lambda s: s

DEFAULT_CURRENCY = getattr(settings, 'DEFAULT_CURRENCY', 'EUR')

WAITTING_PROCESSING = getattr(settings, 'WAITTING_PROCESSING', 'WAITTING_PROCESSING')
WAITTING_CONFIRMATION = getattr(settings, 'WAITTING_CONFIRMATION', 'WAITTING_CONFIRMATION')
CONFIRMED = getattr(settings, 'CONFIRMED', 'CONFIRMED')
REJECTED = getattr(settings, 'REJECTED', 'REJECTED')
LOCKED = getattr(settings, 'LOCKED', 'LOCKED')
DISCARTED = getattr(settings, 'DISCARTED', 'DISCARTED')

PAYMENT_STATUS_CHOICES = getattr(settings, 'PAYMENT_STATUS_CHOICES', (
                          (WAITTING_PROCESSING, (u'Waitting for processing')),
                          (WAITTING_CONFIRMATION, _(u'Waitting for confirmation')),
                          (CONFIRMED, _(u'Confirmed')),
                          (REJECTED, _(u'Rejected')),
                          (LOCKED, _(u'Locked')),
                          (DISCARTED, _(u'Discarted')),))

#PAYMENT_METHODS = getattr(settings, 'PAYMENT_METHODS_CHOICES', (('q19', 'Q19'),
#                                                                ('bank_transfer', _('Bank Transfer')),
#                                                                ('paypal', _('PayPal')),
#                                                                ('visa', _('Visa')),))

DEFAULT_PAYMENT_METHOD = getattr(settings, 'DEFAULT_PAYMENT_METHOD', 'q19')

# You can define custom initial status for each payment method
BANK_TRANSFER_INIATIAL_STATUS = getattr(settings, 'BANK_TRANSFER_INITIAL_STATUS', WAITTING_CONFIRMATION)
DEFAULT_INITIAL_STATUS = getattr(settings, 'DEFAULT_INITIAL_STATUS', WAITTING_PROCESSING)

DEFAULT_OPERATION = getattr(settings, 'DEFAULT_OPERATION', 'all')

#Q19_CODIGO_PRESENTADOR = getattr(settings, 'Q19_', 'G60437761000')
#Q19_NOMBRE_CLIENTE_PRESENTADOR = getattr(settings, 'Q19_NOMBRE_CLIENTE_PRESENTADOR', 'Coordinadora comunicacio per a la cooperacio - Pangea')
#Q19_ENTIDAD_RECEPTORA = getattr(settings, 'Q19_ENTIDAD_RECEPTORA', '3025')
#Q19_OFICINA_RECEPTORA = getattr(settings, 'Q19_OFICINA_RECEPTORA', '0004')


LANGUAGE_CHOICES = getattr(settings, 'LANGUAGE_CHOICES', (('ca', ugettext('Catalan')),
                                                          ('es', ugettext('Spanish')),
                                                          ('en', ugettext('English')),))	                                                                       

DEFAULT_LANGUAGE = getattr(settings, 'DEFAULT_LANGUAGE', 'ca')                                                          

Q19_PRESENTER_CODE = getattr(settings, 'Q19_PRESENTER_CODE', 'G60437761000')
Q19_ORDERER_CODE = getattr(settings, 'Q19_PRESENTER_CODE', 'G60437761000')


METHOD_FILTER_CHOICES = getattr(settings, 'METHOD_FILTER_CHOICES', (('All', _('All')),
                                                                    ('Fee', _('Membership Fee')),
                                                                    ('Invoice', _('Invoice')),))

DEFAULT_METHOD_FILTER = getattr(settings, 'DEFAULT_METHOD_FILTER', 'All')

ALL_EXPRESSION = getattr(settings, 'ALL_EXPRESSION', "True")
FEE_EXPRESSION = getattr(settings, 'FEE_EXPRESSION', "bill.type == 'Fee' or bill.type == 'AmendmentFee'")
INVOICE_EXPRESSION = getattr(settings, 'INVOICE_EXPRESSION', "bill.type == 'Invoice' or bill.type == 'AmendmentInvoice'")
