from orchestra.settings import Setting


# Pluggable backend for bill generation.
ORDERS_BILLING_BACKEND = Setting('ORDERS_BILLING_BACKEND',
    'orchestra.contrib.orders.billing.BillsBackend'
)


# Pluggable service class
ORDERS_SERVICE_MODEL = Setting('ORDERS_SERVICE_MODEL',
    'services.Service'
)


# Prevent inspecting these apps for service accounting
ORDERS_EXCLUDED_APPS = Setting('ORDERS_EXCLUDED_APPS', (
    'orders',
    'admin',
    'contenttypes',
    'auth',
    'migrations',
    'sessions',
    'orchestration',
    'bills',
    'services',
))


# Only account for significative changes
# metric_storage new value: lastvalue*(1+threshold) > currentvalue or lastvalue*threshold < currentvalue
ORDERS_METRIC_ERROR = Setting('ORDERS_METRIC_ERROR',
    0.01
)
