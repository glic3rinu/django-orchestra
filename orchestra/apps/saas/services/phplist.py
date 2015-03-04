from django import forms
from django.utils.translation import ugettext_lazy as _

from .options import SoftwareService, SoftwareServiceForm


class PHPListForm(SoftwareServiceForm):
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={'size':'40'}))


class PHPListService(SoftwareService):
    verbose_name = "phpList"
    form = PHPListForm
    icon = 'orchestra/icons/apps/Phplist.png'
