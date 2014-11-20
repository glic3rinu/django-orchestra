from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .options import SoftwareService, SoftwareServiceForm


class WordPressForm(SoftwareServiceForm):
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={'size':'40'}))


class WordPressDataSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))


class WordPressService(SoftwareService):
    verbose_name = "WordPress"
    form = WordPressForm
    serializer = WordPressDataSerializer
    icon = 'saas/icons/WordPress.png'
    site_name_base_domain = 'blogs.orchestra.lan'
    change_readonly_fileds = ('email',)
