from django import forms
from django.utils.translation import ugettext_lazy as _

from orchestra.forms.widgets import SpanWidget

from .. import settings
from ..forms import SaaSPasswordForm
from .options import SoftwareService


class MoodleForm(SaaSPasswordForm):
    admin_username = forms.CharField(label=_("Admin username"), required=False,
        widget=SpanWidget(display='admin'))


class MoodleService(SoftwareService):
    name = 'moodle'
    verbose_name = "Moodle"
    form = MoodleForm
    description_field = 'site_name'
    icon = 'orchestra/icons/apps/Moodle.png'
    site_domain = settings.SAAS_MOODLE_DOMAIN
    db_name = settings.SAAS_MOODLE_DB_NAME
    db_user = settings.SAAS_MOODLE_DB_USER
