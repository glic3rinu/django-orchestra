from django import forms
from django.utils.translation import ugettext_lazy as _

from orchestra.forms import PluginDataForm

from .options import SoftwareService


class BSCWForm(PluginDataForm):
    username = forms.CharField(label=_("Username"), max_length=64)
    password = forms.CharField(label=_("Password"), max_length=64)
    quota = forms.IntegerField(label=_("Quota"))


class BSCWService(SoftwareService):
    verbose_name = "BSCW"
    form = BSCWForm
    description_field = 'username'
    icon = 'saas/icons/BSCW.png'
