from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from orchestra.api.serializers import HyperlinkedModelSerializer
from orchestra.contrib.accounts.serializers import AccountSerializerMixin
from orchestra.core.validators import validate_password

from .models import List


class RelatedDomainSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = List.address_domain.field.rel.to
        fields = ('url', 'name')
    
    def from_native(self, data, files=None):
        queryset = self.opts.model.objects.filter(account=self.account)
        return get_object_or_404(queryset, name=data['name'])


class ListSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    password = serializers.CharField(max_length=128, label=_('Password'),
            validators=[validate_password], write_only=True, required=False,
            widget=widgets.PasswordInput)
    address_domain = RelatedDomainSerializer(required=False)
    
    class Meta:
        model = List
        fields = ('url', 'name', 'address_name', 'address_domain', 'admin_email')
        postonly_fields = ('name',)
    
    def validate_password(self, attrs, source):
        """ POST only password """
        if self.object:
            if 'password' in attrs:
                raise serializers.ValidationError(_("Can not set password"))
        elif 'password' not in attrs:
            raise serializers.ValidationError(_("Password required"))
        return attrs
    
    def validate_address_domain(self, attrs, source):
        address_domain = attrs.get(source)
        address_name = attrs.get('address_name')
        if self.object:
            address_domain = address_domain or self.object.address_domain
            address_name = address_name or self.object.address_name
        if address_name and not address_domain:
            raise serializers.ValidationError(
                _("address_domains should should be provided when providing an addres_name"))
        return attrs
    
    def save_object(self, obj, **kwargs):
        if not obj.pk:
            obj.set_password(self.init_data.get('password', ''))
        super(ListSerializer, self).save_object(obj, **kwargs)
