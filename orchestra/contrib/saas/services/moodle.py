from django import forms
from django.utils.translation import ugettext_lazy as _

from .options import SoftwareService, SoftwareServiceForm


class MoodleForm(SoftwareServiceForm):
    email = forms.EmailField(label=_("Email"))


class MoodleService(SoftwareService):
    verbose_name = "Moodle"
    form = MoodleForm
    description_field = 'site_name'
    icon = 'orchestra/icons/apps/Moodle.png'
