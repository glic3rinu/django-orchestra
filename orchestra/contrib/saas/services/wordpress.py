from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .options import SoftwareService, SoftwareServiceForm


class WordPressForm(SoftwareServiceForm):
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={'size':'40'}))


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
