from django.apps import AppConfig

from orchestra.core import accounts
from orchestra.utils.db import database_ready


class OrdersConfig(AppConfig):
    name = 'orchestra.contrib.orders'
    verbose_name = 'Orders'
    
    def ready(self):
        from .models import Order
        accounts.register(Order)
        if database_ready():
            from . import signals
