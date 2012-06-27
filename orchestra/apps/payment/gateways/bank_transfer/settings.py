from django.conf import settings
from payment import settings as payment_settings
ugettext = lambda s: s


DEFAULT_INITIAL_STATUS = getattr(settings, 'DEFAULT_INITIAL_STATUS', payment_settings.WAITTING_PROCESSING)
REPORT_TEMPLATE = getattr(settings, 'REPORT_TEMPLATE', 'transfer_report.html')
