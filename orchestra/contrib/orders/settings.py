from orchestra.contrib.settings import Setting


ORDERS_BILLING_BACKEND = Setting('ORDERS_BILLING_BACKEND',
    'orchestra.contrib.orders.billing.BillsBackend',
    validators=[Setting.validate_import_class],
    help_text="Pluggable backend for bill generation.",
)


ORDERS_SERVICE_MODEL = Setting('ORDERS_SERVICE_MODEL',
    'services.Service',
    validators=[Setting.validate_model_label],
    help_text="Pluggable service class.",
)


ORDERS_EXCLUDED_APPS = Setting('ORDERS_EXCLUDED_APPS',
    (
        'orders',
        'admin',
        'contenttypes',
        'auth',
        'migrations',
        'sessions',
        'orchestration',
        'bills',
        'services',
        'mailer',
        'issues',
    ),
    help_text="Prevent inspecting these apps for service accounting."
)


ORDERS_METRIC_ERROR = Setting('ORDERS_METRIC_ERROR',
    0.05,
    help_text=("Only account for significative changes.<br>"
               "metric_storage new value: <tt>lastvalue*(1+threshold) > currentvalue or lastvalue*threshold < currentvalue</tt>."),
)


ORDERS_BILLED_METRIC_CLEANUP_DAYS = Setting('ORDERS_BILLED_METRIC_CLEANUP_DAYS',
    40,
    help_text=("Number of days after a billed stored metric is deleted."),
)
