from django import forms
from django.utils.translation import ugettext_lazy as _

from orchestra.forms import PluginDataForm

from .options import SoftwareService


class DrupalForm(PluginDataForm):
    username = forms.CharField(label=_("Username"), max_length=64)
    password = forms.CharField(label=_("Password"), max_length=64)
    site_name = forms.CharField(label=_("Site name"), max_length=64)
    email = forms.EmailField(label=_("Email"))


class DrupalService(SoftwareService):
    verbose_name = "Drupal"
    form = DrupalForm
    description_field = 'site_name'
