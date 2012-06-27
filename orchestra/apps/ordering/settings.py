from django.conf import settings
from django.utils.translation import ugettext as _

ugettext = lambda s: s

# If your models have a 'contact' field just provide it: 
# if you have a 'contract like' approach see: #TODO: models.contractsignal
#TODO create a custom contact field per model ? or is enough to create a dynamic property on packs in order to respond to this custom field?
#also for contact model provide a dynamic attribute like contact_model.contact: return self ?
CONTACT_MODEL = getattr(settings, 'CONTACT_MODEL', 'contacts.Contact')
CONTACT_FIELD = getattr(settings, 'CONTACT_FIELD', 'contact')

MONTHLY = getattr(settings, 'MONTHLY', 1)
ANUAL = getattr(settings, 'ANUAL', 12)
SIX_MONTHS = getattr(settings, 'MONTHS', 6)
FOUR_MONTHS = getattr(settings, 'MONTHS', 4)
THREE_MONTHS = getattr(settings, 'MONTHS', 3)
TWO_MONTHS = getattr(settings, 'MONTHS', 2)
NO_PERIOD = getattr(settings, 'NO_PERIOD', 0)

PERIOD_CHOICES = getattr(settings, 'PERIOD_CHOICES',(
    (NO_PERIOD, _('No period')),
    (ANUAL, _('Anual')),
    (SIX_MONTHS, _('6 Months')),
    (FOUR_MONTHS, _('4 Months')),
    (THREE_MONTHS, _('3 Months')),
    (TWO_MONTHS, _('2 Months')),                        
    (MONTHLY, _('Monthly')), ))
    

FIXED = getattr(settings, 'FIXED', 1)
VARIABLE = getattr(settings, 'VARIABLE', 2)

POINT_CHOICES = getattr(settings, 'POINT_CHOICES',(
    (NO_PERIOD, _('No Period')),
    (FIXED, _('Fixed')),
    (VARIABLE, _('Variable')),))


CURRENT = getattr(settings, 'CURRENT', 1)
EVERY = getattr(settings, 'EVERY', 2)

PRICING_EFFECT_CHOICES = getattr(settings, 'PRICING_EFFECT_CHOICES',(
    (NO_PERIOD, _('No period')),
    (CURRENT, _('Current on register or renew')),
    (EVERY, _('Every period')),))


#ENTAIR = getattr(settings, 'ENTAIR', 'E')    
DISCOUNT_ON_REGISTER = getattr(settings, 'DISCOUNT_ON_REGISTER', 'R')
DISCOUNT_ON_CANCEL = getattr(settings, 'DISCOUNT_ON_CANCEL', 'C')
DISCOUNT_ON_DISABLE = getattr(settings, 'DISCOUNT_ON_DISABLE', 'D')

DISCOUNT_CHOICES = getattr(settings, 'DISCOUNT_CHOICES',(
    #(ENTAIR, _('No discount')),
    (DISCOUNT_ON_REGISTER, _('Discount on Register')),
    (DISCOUNT_ON_CANCEL, _('Discount on Cancel')),
    (DISCOUNT_ON_DISABLE, _('Discount on Disable')),))

REFOUND_ON_CANCEL = getattr(settings, 'REFOUNT_ON_CANCEL', 'C')
RECHARGE_ON_CANCEL = getattr(settings, 'RECHARGE_ON_CANCEL', 'A')
REFOUND_ON_DISABLE = getattr(settings, 'REFOUND_ON_DISABLE', 'D')
RECHARGE_ON_DISABLE = getattr(settings, 'RECHARGE_ON_DISABLE', 'CD')
REFOUND_ON_WEIGHT = getattr(settings, 'REFOUND_ON_WEIGHT', 'FM')
RECHARGE_ON_WEIGHT = getattr(settings, 'RECHARGE_ON_WEIGHT', 'CR')

ON_PREPAY_CHOICES = getattr(settings, 'ON_PREPAY_CHOICES',(
    (REFOUND_ON_CANCEL, _('Refound on Cancel')),
    (RECHARGE_ON_CANCEL, _('Recharge on Cancel')),
    (REFOUND_ON_DISABLE, _('Refound on Disable')),
    (RECHARGE_ON_DISABLE, _('Recharge on Disable')),
    (REFOUND_ON_WEIGHT, _('Refound on Weight')),
    (RECHARGE_ON_WEIGHT, _('Recharge on Weight')),))

EVENTUAL = getattr(settings, 'EVENTUAL', 'E')
POSTPAY = getattr(settings, 'POSTPAY', 'O')
PREPAY = getattr(settings, 'PREPAY', 'P')
#PREPAY_WITH_RECHARGE = getattr(settings, 'PREPAY_WITH_RECHARGE', 'A')
#PREPAY_WITH_REFOUND = getattr(settings, 'PREPAY_WITH_REFOUND', 'F')
#PREPAY_WITH_RECHARGE_AND_REFOUND = getattr(settings, 'PREPAY_WITH_RECHARGE_AND_REFOUND', 'W')

PAYMENT_CHOICES = getattr(settings, 'PAYMENT_CHOICES',(
    (EVENTUAL, _('Eventual')),    
    (POSTPAY, _('Postpay')),
    (PREPAY, _('Prepay')),))
    

#    (PREPAY_WITH_RECHARGE, _('Prepay with recharge')),
#    (PREPAY_WITH_REFOUND, _('Prepay with refound')),   
#    (PREPAY_WITH_RECHARGE_AND_REFOUND, _('Prepay with recharge and refound')),))


ORDERS = getattr(settings, 'ORDERS', 'O')
WEIGHT = getattr(settings, 'WEIGHT', 'W')

PRICING_WITH_CHOICES = getattr(settings, 'PRICING_WITH_CHOICES',(
    (ORDERS, _('Number of Orders')),
    (WEIGHT, _('Weight of Service')),))


NO_ORDERS = getattr(settings, 'NO_ORDERS', '0')
ACTIVE = getattr(settings, 'ACTIVE', 'A')
#TODO: deprecate this shit
ACTIVE_OR_BILLED = getattr(settings, 'ACTIVE_OR_BILLEDs', 'B')
RENEWED = getattr(settings, 'RENEWED', 'W')
REGISTRED = getattr(settings, 'REGISTRED', 'G')
REGISTRED_OR_RENEWED = getattr(settings, 'REGISTRED_OR_RENEWED', 'R')  

        
ORDERS_WITH_CHOICES = getattr(settings, 'ORDERS_WITH_CHOICES',(
    (NO_ORDERS, _('Pricing with weight')),
    (ACTIVE, _('Active')),
    (RENEWED, _('Renewed')),
    (REGISTRED, _('Registred')),
    (REGISTRED_OR_RENEWED, _('Registred or Renewed')),))    
    

NO_WEIGHT = getattr(settings, 'NO_WEIGHT', '0')
SINGLE_ORDER = getattr(settings, 'SINGLE_ORDER', 'S')
ALL_CONTACT_ORDERS = getattr(settings, 'ALL_CONTACT_ORDERS', 'A')

WEIGHT_WITH_CHOICES = getattr(settings, 'WEIGHT_WITH_CHOICES',(
    (NO_WEIGHT, _('Pricing with Orders')),
    (SINGLE_ORDER, _('Single Order')),
    (ALL_CONTACT_ORDERS, _('All Contact Orders')),))
    

BEST = getattr(settings, 'BEST', 'B')
CONSERVATIVE = getattr(settings, 'CONSERVATIVE', 'C')

RATING_CHOICES = getattr(settings, 'RATING_CHOICES',(
    (BEST, _('Best Price')),
    (CONSERVATIVE, _('Conservative Price')),))


CHANGES = getattr(settings, 'CHANGES', 'Changes')
LAST = getattr(settings, 'LAST', 'Last')
SUM = getattr(settings, 'SUM', 'Sum')
MIN = getattr(settings, 'MIN', 'Max')
MAX = getattr(settings, 'MIN', 'Min')
AVG = getattr(settings, 'AVG', 'Avg')

METRIC_GET_CHOICES = getattr(settings, 'METRIC_GET_CHOICES',(
    (CHANGES, _('Changes')),
    (LAST, _('LAST(Pricing Period)')),
    (SUM, _('SUM(Pricing Period)')),
    (MIN, _('MIN(Pricing Period)')),        
    (MAX, _('MAX(Pricing Period)')),
    (AVG, _('AVG(Pricing Period)')), ))

# Pricing stuff
DEFAULT_PRICING_PERIOD = getattr(settings, 'DEFAULT_PRICING_PERIOD', NO_PERIOD)
DEFAULT_PRICING_POINT = getattr(settings, 'DEFAULT_PRICING_POINT', NO_PERIOD)    
DEFAULT_PRICING_EFFECT = getattr(settings, 'DEFAULT_PRICING_EFFECT', NO_PERIOD)
DEFAULT_PRICING_WITH = getattr(settings, 'DEFAULT_PRICING_WITH', ORDERS)
DEFAULT_ORDERS_WITH = getattr(settings, 'DEFAULT_ORDERS_WITH', ACTIVE)
DEFAULT_WEIGHT_WITH = getattr(settings, 'DEFAULT_WEIGHT_WITH', NO_WEIGHT)  
DEFAULT_RATING = getattr(settings, 'DEFAULT_RATING', BEST)    
DEFAULT_METRIC_GET = getattr(settings, 'DEFAULT_METRIC_GET', '')
# Billing Stuff
DEFAULT_BILLING_PERIOD = getattr(settings, 'DEFAULT_BILLING_PERIOD', ANUAL)
DEFAULT_BILLING_POINT = getattr(settings, 'DEFAULT_BILLING_POINT', FIXED)
DEFAULT_PAYMENT = getattr(settings, 'DEFAULT_PAYMENT', PREPAY)
DEFAULT_DISCOUNT = getattr(settings, 'DEFAULT_DISCOUNT', [DISCOUNT_ON_REGISTER, DISCOUNT_ON_CANCEL, DISCOUNT_ON_DISABLE] )
DEFAULT_ON_PREPAY = getattr(settings, 'DEFAULT_ON_PREPAY', [RECHARGE_ON_WEIGHT])
ANUAL_RENEW_MONTH = getattr(settings, 'ANUAL_RENEW_MONTH', 4)
SIX_MONTHS_RENEW_MONTH = getattr(settings, 'SIX_MONTHS_RENEW_MONTH', 1)
FOUR_MONTHS_RENEW_MONTH = getattr(settings, 'FOUR_MONTHS_RENEW_MONTH', 1)
THREE_MONTHS_RENEW_MONTH = getattr(settings, 'THREE_MONTHS_RENEW_MONTH', 1)
TWO_MONTHS_RENEW_MONTH = getattr(settings, 'TWO_MONTHS_RENEW_MONTH', 1)

DEFAULT_IS_FEE = getattr(settings, 'DEFAULT_IS_FEE', False)
DEFAULT_TAX_PK = getattr(settings, 'DEFAULT_TAX_PK', 1)



    

