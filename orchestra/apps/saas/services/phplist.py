from django import forms
from django.utils.translation import ugettext_lazy as _

from orchestra.forms import PluginDataForm

from .options import SoftwareService


class PHPListForm(PluginDataForm):
    email = forms.EmailField(label=_("Email"))


class PHPListService(SoftwareService):
    verbose_name = "phpList"
    form = PHPListForm
    description_field = 'email'
