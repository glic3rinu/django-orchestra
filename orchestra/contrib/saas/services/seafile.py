from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from .. import settings
from ..forms import SaaSPasswordForm
from .options import SoftwareService


# TODO monitor quota since out of sync?

class SeaFileForm(SaaSPasswordForm):
    email = forms.EmailField(label=_("Email"), widget=forms.TextInput(attrs={'size':'40'}))
    quota = forms.IntegerField(label=_("Quota"), initial=settings.SAAS_SEAFILE_DEFAULT_QUOTA,
            help_text=_("Disk quota in MB."))


class SeaFileDataSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    quota = serializers.IntegerField(label=_("Quota"), default=settings.SAAS_SEAFILE_DEFAULT_QUOTA,
            help_text=_("Disk quota in MB."))


class SeaFileService(SoftwareService):
    name = 'seafile'
    verbose_name = "SeaFile"
    form = SeaFileForm
    serializer = SeaFileDataSerializer
    icon = 'orchestra/icons/apps/seafile.png'
    site_domain = settings.SAAS_SEAFILE_DOMAIN
    change_readonly_fields = ('email',)
