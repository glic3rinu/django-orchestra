from django.apps import AppConfig

from orchestra.core import accounts


class BillsConfig(AppConfig):
    name = 'orchestra.contrib.bills'
    verbose_name = 'Bills'
    
    def ready(self):
        from .models import Bill
        accounts.register(Bill, icon='invoice.png')
