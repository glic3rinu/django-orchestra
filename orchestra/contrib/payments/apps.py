from django.apps import AppConfig

from orchestra.core import accounts


class PaymentsConfig(AppConfig):
    name = 'orchestra.contrib.payments'
    verbose_name = "Payments"
    
    def ready(self):
        from .models import PaymentSource, Transaction, TransactionProcess
        accounts.register(PaymentSource, dashboard=False)
        accounts.register(Transaction, icon='transaction.png', search=False)
        accounts.register(TransactionProcess, icon='transactionprocess.png', dashboard=False, search=False)
