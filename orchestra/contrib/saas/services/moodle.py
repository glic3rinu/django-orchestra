from django import forms
from django.utils.translation import ugettext_lazy as _

from ..forms import SaaSPasswordForm
from .options import SoftwareService


class MoodleForm(SaaSPasswordForm):
    email = forms.EmailField(label=_("Email"))


class MoodleService(SoftwareService):
    verbose_name = "Moodle"
    form = MoodleForm
    description_field = 'site_name'
    icon = 'orchestra/icons/apps/Moodle.png'
