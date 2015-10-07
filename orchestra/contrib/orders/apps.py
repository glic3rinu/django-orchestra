from django.apps import AppConfig

from orchestra.core import accounts


class OrdersConfig(AppConfig):
    name = 'orchestra.contrib.orders'
    verbose_name = 'Orders'
    
    def ready(self):
        from .models import Order
        accounts.register(Order, icon='basket.png', search=False)
        from . import signals
