from django.forms import widgets
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.api.serializers import SetPasswordHyperlinkedSerializer
from orchestra.contrib.accounts.serializers import AccountSerializerMixin

from .models import Mailbox, Address


class RelatedDomainSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address.domain.field.rel.to
        fields = ('url', 'id', 'name')
    
    def from_native(self, data, files=None):
        queryset = self.opts.model.objects.filter(account=self.account)
        return get_object_or_404(queryset, name=data['name'])


class RelatedAddressSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    domain = RelatedDomainSerializer()
    
    class Meta:
        model = Address
        fields = ('url', 'id', 'name', 'domain', 'forward')
#    
#    def from_native(self, data, files=None):
#        queryset = self.opts.model.objects.filter(account=self.account)
#        return get_object_or_404(queryset, name=data['name'])


class MailboxSerializer(AccountSerializerMixin, SetPasswordHyperlinkedSerializer):
    addresses = RelatedAddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = Mailbox
        fields = (
            'url', 'id', 'name', 'password', 'filtering', 'custom_filtering', 'addresses', 'is_active'
        )
        postonly_fields = ('name', 'password')


class RelatedMailboxSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mailbox
        fields = ('url', 'id', 'name')
    
    def from_native(self, data, files=None):
        queryset = self.opts.model.objects.filter(account=self.account)
        return get_object_or_404(queryset, name=data['name'])


class AddressSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    domain = RelatedDomainSerializer()
    mailboxes = RelatedMailboxSerializer(many=True, required=False) #allow_add_remove=True
    
    class Meta:
        model = Address
        fields = ('url', 'id', 'name', 'domain', 'mailboxes', 'forward')
    
    def validate(self, attrs):
        attrs = super(AddressSerializer, self).validate(attrs)
        if not attrs['mailboxes'] and not attrs['forward']:
            raise serializers.ValidationError("A mailbox or forward address should be provided.")
        return attrs
