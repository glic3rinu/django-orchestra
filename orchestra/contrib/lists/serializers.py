from django.core.validators import RegexValidator
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.api.serializers import SetPasswordHyperlinkedSerializer, RelatedHyperlinkedModelSerializer
from orchestra.contrib.accounts.serializers import AccountSerializerMixin
from orchestra.core.validators import validate_password

from .models import List


class RelatedDomainSerializer(AccountSerializerMixin, RelatedHyperlinkedModelSerializer):
    class Meta:
        model = List.address_domain.field.rel.to
        fields = ('url', 'id', 'name')


class ListSerializer(AccountSerializerMixin, SetPasswordHyperlinkedSerializer):
    password = serializers.CharField(max_length=128, label=_('Password'),
        write_only=True, style={'widget': widgets.PasswordInput},
        validators=[
            validate_password,
            RegexValidator(r'^[^"\'\\]+$',
                           _('Enter a valid password. '
                             'This value may contain any ascii character except for '
                             ' \'/"/\\/ characters.'), 'invalid'),
        ])
    
    address_domain = RelatedDomainSerializer(required=False)
    
    class Meta:
        model = List
        fields = ('url', 'id', 'name', 'password', 'address_name', 'address_domain', 'admin_email', 'is_active',)
        postonly_fields = ('name', 'password')
    
    def validate_address_domain(self, address_name):
        if self.instance:
            address_domain = address_domain or self.instance.address_domain
            address_name = address_name or self.instance.address_name
        if address_name and not address_domain:
            raise serializers.ValidationError(
                _("address_domains should should be provided when providing an addres_name"))
        return address_name
