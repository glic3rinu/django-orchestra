from django.utils.translation import ugettext_lazy as _
from djcelery.admin import PeriodicTaskAdmin

from orchestra.admin.utils import admin_date


display_last_run_at = admin_date('last_run_at', short_description=_("Last run"))

PeriodicTaskAdmin.list_display = ('__unicode__', display_last_run_at, 'total_run_count', 'enabled')
