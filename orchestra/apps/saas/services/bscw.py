from django import forms
from django.utils.translation import ugettext_lazy as _

from .options import SoftwareService, SoftwareServiceForm


class BSCWForm(SoftwareServiceForm):
    quota = forms.IntegerField(label=_("Quota"))


class BSCWService(SoftwareService):
    verbose_name = "BSCW"
    form = BSCWForm
    description_field = 'username'
