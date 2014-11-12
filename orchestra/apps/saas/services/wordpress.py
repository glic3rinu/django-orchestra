from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.plugins.forms import PluginDataForm

from .options import SoftwareService


class WordPressForm(PluginDataForm):
    username = forms.CharField(label=_("Username"), max_length=64)
    password = forms.CharField(label=_("Password"), max_length=64)
    site_name = forms.CharField(label=_("Site name"), max_length=64,
        help_text=_("URL will be &lt;site_name&gt;.blogs.orchestra.lan"))
    email = forms.EmailField(label=_("Email"))
    
    def __init__(self, *args, **kwargs):
        super(WordPressForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            url = 'http://%s.%s' % (instance.data['site_name'], 'blogs.orchestra.lan')
            url = '<a href="%s">%s</a>' % (url, url)
            self.fields['site_name'].help_text = mark_safe(url)


class WordPressService(SoftwareService):
    verbose_name = "WordPress"
    form = WordPressForm
    description_field = 'site_name'
    icon = 'saas/icons/WordPress.png'
