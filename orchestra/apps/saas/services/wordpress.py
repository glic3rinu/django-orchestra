from django import forms
from django.utils.translation import ugettext_lazy as _

from orchestra.forms import PluginDataForm

from .options import SoftwareService


class WordpressForm(PluginDataForm):
    username = forms.CharField(label=_("Username"), max_length=64)
    password = forms.CharField(label=_("Password"), max_length=64)
    site_name = forms.CharField(label=_("Site name"), max_length=64,
        help_text=_("URL will be &lt;site_name&gt;.blogs.orchestra.lan"))
    email = forms.EmailField(label=_("Email"))


class WordpressService(SoftwareService):
    verbose_name = "WordPress"
    form = WordpressForm
    description_field = 'site_name'
    icon = 'saas/icons/WordPress.png'
