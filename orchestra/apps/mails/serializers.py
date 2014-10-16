from django.forms import widgets
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import serializers

from orchestra.api.serializers import HyperlinkedModelSerializer
from orchestra.apps.accounts.serializers import AccountSerializerMixin
from orchestra.core.validators import validate_password

from .models import Mailbox, Address


class MailboxSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    password = serializers.CharField(max_length=128, label=_('Password'),
            validators=[validate_password], write_only=True, required=False,
            widget=widgets.PasswordInput)
    
    class Meta:
        model = Mailbox
        fields = (
            'url', 'name', 'password', 'filtering', 'custom_filtering', 'addresses', 'is_active'
        )
        postonly_fields = ('name',)
    
    def validate_password(self, attrs, source):
        """ POST only password """
        if self.object:
            if 'password' in attrs:
                raise serializers.ValidationError(_("Can not set password"))
        elif 'password' not in attrs:
            raise serializers.ValidationError(_("Password required"))
        return attrs
    
    def save_object(self, obj, **kwargs):
        # FIXME this method will be called when saving nested serializers :(
        if not obj.pk:
            obj.set_password(obj.password)
        super(MailboxSerializer, self).save_object(obj, **kwargs)


class RelatedMailboxSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mailbox
        fields = ('url', 'name')
    
    def from_native(self, data, files=None):
        queryset = self.opts.model.objects.filter(account=self.account)
        return get_object_or_404(queryset, name=data['name'])


class RelatedDomainSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address.domain.field.rel.to
        fields = ('url', 'name')
    
    def from_native(self, data, files=None):
        queryset = self.opts.model.objects.filter(account=self.account)
        return get_object_or_404(queryset, name=data['name'])


class AddressSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    domain = RelatedDomainSerializer()
    mailboxes = RelatedMailboxSerializer(many=True, allow_add_remove=True, required=False)
    
    class Meta:
        model = Address
        fields = ('url', 'name', 'domain', 'mailboxes', 'forward')
    
    def validate(self, attrs):
        if not attrs['mailboxes'] and not attrs['forward']:
            raise serializers.ValidationError("mailboxes or forward addresses should be provided")
        return attrs
