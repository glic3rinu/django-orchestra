from django.forms import widgets
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.api.serializers import SetPasswordHyperlinkedSerializer
from orchestra.contrib.accounts.serializers import AccountSerializerMixin
from orchestra.core import validators

from .models import SaaS


class SaaSSerializer(AccountSerializerMixin, SetPasswordHyperlinkedSerializer):
    data = serializers.DictField(required=False)
    password = serializers.CharField(write_only=True, required=False,
        style={'widget': widgets.PasswordInput},
        validators=[
            validators.validate_password,
            RegexValidator(r'^[^"\'\\]+$',
                           _('Enter a valid password. '
                             'This value may contain any ascii character except for '
                             ' \'/"/\\/ characters.'), 'invalid'),
        ])
    
    class Meta:
        model = SaaS
        fields = ('url', 'id', 'name', 'service', 'is_active', 'data', 'password')
        postonly_fields = ('name', 'service', 'password')
