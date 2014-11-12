from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.apps.plugins.forms import PluginDataForm
from orchestra.core import validators

from .options import SoftwareService


# TODO monitor quota since out of sync?

class BSCWForm(PluginDataForm):
    username = forms.CharField(label=_("Username"), max_length=64)
    password = forms.CharField(label=_("Password"), max_length=256, required=False)
    email = forms.EmailField(label=_("Email"))
    quota = forms.IntegerField(label=_("Quota"), help_text=_("Disk quota in MB."))


class SEPADirectDebitSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"), max_length=64,
            validators=[validators.validate_name])
    password = serializers.CharField(label=_("Password"), max_length=256, required=False,
            write_only=True)
    email = serializers.EmailField(label=_("Email"))
    quota = serializers.IntegerField(label=_("Quota"), help_text=_("Disk quota in MB."))
    
    def validate(self, data):
        data['username'] = data['username'].strip()
        return data


class BSCWService(SoftwareService):
    verbose_name = "BSCW"
    form = BSCWForm
    serializer = SEPADirectDebitSerializer
    description_field = 'username'
    icon = 'saas/icons/BSCW.png'
    
    @classmethod
    def clean_data(cls, saas):
        try:
            data = super(BSCWService, cls).clean_data(saas)
        except ValidationError, error:
            if not saas.pk and 'password' not in saas.data:
                error.error_dict['password'] = [_("Password is required.")]
            raise error
        if not saas.pk and 'password' not in saas.data:
            raise ValidationError({
                'password': _("Password is required.")
            })
        return data
