from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.settings import Setting


SERVICES_SERVICE_TAXES = Setting('SERVICES_SERVICE_TAXES',
    (
        (0, _("Duty free")),
        (21, "21%"),
    ),
    validators=[Setting.validate_choices]
)


SERVICES_SERVICE_DEFAULT_TAX = Setting('SERVICES_SERVICE_DEFAULT_TAX',
    0,
    choices=SERVICES_SERVICE_TAXES
)


SERVICES_SERVICE_ANUAL_BILLING_MONTH = Setting('SERVICES_SERVICE_ANUAL_BILLING_MONTH',
    1,
    choices=tuple(enumerate(
        ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'), 1))
)


SERVICES_ORDER_MODEL = Setting('SERVICES_ORDER_MODEL',
    'orders.Order',
    validators=[Setting.validate_model_label]
)


SERVICES_RATE_CLASS = Setting('SERVICES_RATE_CLASS',
    'orchestra.contrib.plans.models.Rate',
    validators=[Setting.validate_import_class]
)


SERVICES_DEFAULT_IGNORE_PERIOD = Setting('SERVICES_DEFAULT_IGNORE_PERIOD',
    'TEN_DAYS'
)


SERVICES_IGNORE_ACCOUNT_TYPE = Setting('SERVICES_IGNORE_ACCOUNT_TYPE',
    (
        'superuser',
        'STAFF',
        'FRIEND',
    ),
)
