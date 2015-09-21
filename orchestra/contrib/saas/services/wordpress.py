from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .options import SoftwareService
from ..forms import SaaSBaseForm


class WordPressForm(SaaSBaseForm):
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={'size':'40'}),
        help_text=_("A new user will be created if the above email address is not in the database.<br>"
                    "The username and password will be mailed to this email address."))
    
    def __init__(self, *args, **kwargs):
        super(WordPressForm, self).__init__(*args, **kwargs)
        if self.is_change:
            admin_url = 'http://%s/wp-admin/' % self.instance.get_site_domain()
            help_text = 'Admin URL: <a href="{0}">{0}</a>'.format(admin_url)
            self.fields['site_url'].help_text = mark_safe(help_text)


class WordPressDataSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))


class WordPressService(SoftwareService):
    name = 'wordpress'
    verbose_name = "WordPress"
    form = WordPressForm
    serializer = WordPressDataSerializer
    icon = 'orchestra/icons/apps/WordPress.png'
    change_readonly_fileds = ('email',)
    
    @property
    def site_base_domain(self):
        from .. import settings
        return settings.SAAS_WORDPRESS_BASE_DOMAIN
