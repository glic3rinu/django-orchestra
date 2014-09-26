from django.conf import settings


ORDERS_BILLING_BACKEND = getattr(settings, 'ORDERS_BILLING_BACKEND',
        'orchestra.apps.orders.billing.BillsBackend')


ORDERS_SERVICE_MODEL = getattr(settings, 'ORDERS_SERVICE_MODEL', 'services.Service')
