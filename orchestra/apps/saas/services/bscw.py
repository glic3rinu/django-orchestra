from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .. import settings
from .options import SoftwareService, SoftwareServiceForm


# TODO monitor quota since out of sync?

class BSCWForm(SoftwareServiceForm):
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={'size':'40'}))
    quota = forms.IntegerField(label=_("Quota"), initial=settings.SAAS_BSCW_DEFAULT_QUOTA,
            help_text=_("Disk quota in MB."))


class BSCWDataSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    quota = serializers.IntegerField(label=_("Quota"), default=settings.SAAS_BSCW_DEFAULT_QUOTA,
            help_text=_("Disk quota in MB."))


class BSCWService(SoftwareService):
    name = 'bscw'
    verbose_name = "BSCW"
    form = BSCWForm
    serializer = BSCWDataSerializer
    icon = 'orchestra/icons/apps/BSCW.png'
    # TODO override from settings
    site_domain = settings.SAAS_BSCW_DOMAIN
    change_readonly_fileds = ('email',)
