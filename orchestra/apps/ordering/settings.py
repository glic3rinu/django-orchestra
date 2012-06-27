from django.conf import settings
from django.utils.translation import ugettext as _

ugettext = lambda s: s

# If your models have a 'contact' field just provide it: 
# if you have a 'contract like' approach see: #TODO: models.contractsignal
#TODO create a custom contact field per model ? or is enough to create a dynamic property on packs in order to respond to this custom field?
#also for contact model provide a dynamic attribute like contact_model.contact: return self ?
ORDERING_CONTACT_MODEL = getattr(settings, 'ORDERING_CONTACT_MODEL', 'contacts.Contact')
ORDERING_CONTACT_FIELD = getattr(settings, 'ORDERING_CONTACT_FIELD', 'contact')

MONTHLY =  1
ANUAL = 12
SIX_MONTHS = 6
FOUR_MONTHS = 4
THREE_MONTHS = 3
TWO_MONTHS = 2
NO_PERIOD = 0

ORDERING_PERIOD_CHOICES = getattr(settings, 'ORDERING_PERIOD_CHOICES',(
    (NO_PERIOD, _('No period')),
    (ANUAL, _('Anual')),
    (SIX_MONTHS, _('6 Months')),
    (FOUR_MONTHS, _('4 Months')),
    (THREE_MONTHS, _('3 Months')),
    (TWO_MONTHS, _('2 Months')),
    (MONTHLY, _('Monthly')), ))

FIXED = 1
VARIABLE = 2

ORDERING_POINT_CHOICES = getattr(settings, 'ORDERING_POINT_CHOICES',(
    (NO_PERIOD, _('No Period')),
    (FIXED, _('Fixed')),
    (VARIABLE, _('Variable')),))


CURRENT = 1
EVERY = 2

ORDERING_PRICING_EFFECT_CHOICES = getattr(settings, 'ORDERING_PRICING_EFFECT_CHOICES',(
    (NO_PERIOD, _('No period')),
    (CURRENT, _('Current on register or renew')),
    (EVERY, _('Every period')),))


DISCOUNT_ON_REGISTER = 'R'
DISCOUNT_ON_CANCEL = 'C'
DISCOUNT_ON_DISABLE = 'D'

ORDERING_DISCOUNT_CHOICES = getattr(settings, 'ORDERING_DISCOUNT_CHOICES',(
    (DISCOUNT_ON_REGISTER, _('Discount on Register')),
    (DISCOUNT_ON_CANCEL, _('Discount on Cancel')),
    (DISCOUNT_ON_DISABLE, _('Discount on Disable')),))

REFOUND_ON_CANCEL = 'C'
RECHARGE_ON_CANCEL = 'A'
REFOUND_ON_DISABLE = 'D'
RECHARGE_ON_DISABLE = 'CD'
REFOUND_ON_WEIGHT = 'FM'
RECHARGE_ON_WEIGHT = 'CR'

ORDERING_ON_PREPAY_CHOICES = getattr(settings, 'ORDERING_ON_PREPAY_CHOICES',(
    (REFOUND_ON_CANCEL, _('Refound on Cancel')),
    (RECHARGE_ON_CANCEL, _('Recharge on Cancel')),
    (REFOUND_ON_DISABLE, _('Refound on Disable')),
    (RECHARGE_ON_DISABLE, _('Recharge on Disable')),
    (REFOUND_ON_WEIGHT, _('Refound on Weight')),
    (RECHARGE_ON_WEIGHT, _('Recharge on Weight')),))

EVENTUAL = 'E'
POSTPAY = 'O'
PREPAY = 'P'

ORDERING_PAYMENT_CHOICES = getattr(settings, 'ORDERING_PAYMENT_CHOICES',(
    (EVENTUAL, _('Eventual')),    
    (POSTPAY, _('Postpay')),
    (PREPAY, _('Prepay')),))


ORDERS = getattr(settings, 'ORDERS', 'O')
WEIGHT = getattr(settings, 'WEIGHT', 'W')

ORDERING_PRICING_WITH_CHOICES = getattr(settings, 'ORDERING_PRICING_WITH_CHOICES',(
    (ORDERS, _('Number of Orders')),
    (WEIGHT, _('Weight of Service')),))


NO_ORDERS = '0'
ACTIVE = 'A'
#TODO: deprecate this shit
ACTIVE_OR_BILLED = 'B'
RENEWED = 'W'
REGISTRED = 'G'
REGISTRED_OR_RENEWED = 'R'

ORDERING_ORDERS_WITH_CHOICES = getattr(settings, 'ORDERING_ORDERS_WITH_CHOICES',(
    (NO_ORDERS, _('Pricing with weight')),
    (ACTIVE, _('Active')),
    (RENEWED, _('Renewed')),
    (REGISTRED, _('Registred')),
    (REGISTRED_OR_RENEWED, _('Registred or Renewed')),))    
    

NO_WEIGHT = '0'
SINGLE_ORDER = 'S'
ALL_CONTACT_ORDERS = 'A'

ORDERING_WEIGHT_WITH_CHOICES = getattr(settings, 'ORDERING_WEIGHT_WITH_CHOICES',(
    (NO_WEIGHT, _('Pricing with Orders')),
    (SINGLE_ORDER, _('Single Order')),
    (ALL_CONTACT_ORDERS, _('All Contact Orders')),))
    

BEST = 'B'
CONSERVATIVE = 'C'

ORDERING_RATING_CHOICES = getattr(settings, 'ORDERING_RATING_CHOICES',(
    (BEST, _('Best Price')),
    (CONSERVATIVE, _('Conservative Price')),))


CHANGES = 'Changes'
LAST = 'Last'
SUM = 'Sum'
MIN = 'Max'
MAX = 'Min'
AVG = 'Avg'

ORDERING_METRIC_GET_CHOICES = getattr(settings, 'ORDERING_METRIC_GET_CHOICES',(
    (CHANGES, _('Changes')),
    (LAST, _('LAST(Pricing Period)')),
    (SUM, _('SUM(Pricing Period)')),
    (MIN, _('MIN(Pricing Period)')),        
    (MAX, _('MAX(Pricing Period)')),
    (AVG, _('AVG(Pricing Period)')), ))

# Pricing stuff
ORDERING_DEFAULT_PRICING_PERIOD = getattr(settings, 'ORDERING_DEFAULT_PRICING_PERIOD', NO_PERIOD)
ORDERING_DEFAULT_PRICING_POINT = getattr(settings, 'ORDERING_DEFAULT_PRICING_POINT', NO_PERIOD)    
ORDERING_DEFAULT_PRICING_EFFECT = getattr(settings, 'ORDERING_DEFAULT_PRICING_EFFECT', NO_PERIOD)
ORDERING_DEFAULT_PRICING_WITH = getattr(settings, 'ORDERING_DEFAULT_PRICING_WITH', ORDERS)
ORDERING_DEFAULT_ORDERS_WITH = getattr(settings, 'ORDERING_DEFAULT_ORDERS_WITH', ACTIVE)
ORDERING_DEFAULT_WEIGHT_WITH = getattr(settings, 'ORDERING_DEFAULT_WEIGHT_WITH', NO_WEIGHT)  
ORDERING_DEFAULT_RATING = getattr(settings, 'ORDERING_DEFAULT_RATING', BEST)    
ORDERING_DEFAULT_METRIC_GET = getattr(settings, 'ORDERING_DEFAULT_METRIC_GET', '')
# Billing Stuff
ORDERING_DEFAULT_BILLING_PERIOD = getattr(settings, 'ORDERING_DEFAULT_BILLING_PERIOD', ANUAL)
ORDERING_DEFAULT_BILLING_POINT = getattr(settings, 'ORDERING_DEFAULT_BILLING_POINT', FIXED)
ORDERING_DEFAULT_PAYMENT = getattr(settings, 'ORDERING_DEFAULT_PAYMENT', PREPAY)
ORDERING_DEFAULT_DISCOUNT = getattr(settings, 'ORDERING_DEFAULT_DISCOUNT', [DISCOUNT_ON_REGISTER, DISCOUNT_ON_CANCEL, DISCOUNT_ON_DISABLE] )
ORDERING_DEFAULT_ON_PREPAY = getattr(settings, 'ORDERING_DEFAULT_ON_PREPAY', [RECHARGE_ON_WEIGHT])
ORDERING_ANUAL_RENEW_MONTH = getattr(settings, 'ORDERING_ANUAL_RENEW_MONTH', 4)
ORDERING_SIX_MONTHS_RENEW_MONTH = getattr(settings, 'ORDERING_SIX_MONTHS_RENEW_MONTH', 1)
ORDERING_FOUR_MONTHS_RENEW_MONTH = getattr(settings, 'ORDERING_FOUR_MONTHS_RENEW_MONTH', 1)
ORDERING_THREE_MONTHS_RENEW_MONTH = getattr(settings, 'ORDERING_THREE_MONTHS_RENEW_MONTH', 1)
ORDERING_TWO_MONTHS_RENEW_MONTH = getattr(settings, 'ORDERING_TWO_MONTHS_RENEW_MONTH', 1)

ORDERING_DEFAULT_IS_FEE = getattr(settings, 'ORDERING_DEFAULT_IS_FEE', False)
ORDERING_DEFAULT_TAX_PK = getattr(settings, 'ORDERING_DEFAULT_TAX_PK', 1)

