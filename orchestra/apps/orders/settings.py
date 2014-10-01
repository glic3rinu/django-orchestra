from django.conf import settings


ORDERS_BILLING_BACKEND = getattr(settings, 'ORDERS_BILLING_BACKEND',
        'orchestra.apps.orders.billing.BillsBackend')


ORDERS_SERVICE_MODEL = getattr(settings, 'ORDERS_SERVICE_MODEL', 'services.Service')


ORDERS_EXCLUDED_APPS = getattr(settings, 'ORDERS_EXCLUDED_APPS', (
    'orders',
    'admin',
    'contenttypes',
    'auth',
    'migrations',
    'sessions',
    'orchestration',
    'bills',
    # Do not put services here (plans)
))
