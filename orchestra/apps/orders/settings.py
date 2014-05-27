from django.conf import settings
from django.utils.translation import ugettext_lazy as _


ORDERS_PRICE_MODEL = getattr(settings, 'ORDERS_PRICE_MODEL', 'prices.Price')
