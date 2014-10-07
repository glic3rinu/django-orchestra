from rest_framework import serializers

from orchestra.apps.accounts.serializers import AccountSerializerMixin

from .models import Mailbox, Address


class MailboxSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mailbox
        # TODO 'use_custom_filtering', 
        fields = ('url', 'name', 'password', 'custom_filtering', 'addresses', 'is_active')
    
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


class AddressSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address
        fields = ('url', 'name', 'domain', 'mailboxes', 'forward')
    
    def get_fields(self, *args, **kwargs):
        fields = super(AddressSerializer, self).get_fields(*args, **kwargs)
        account = self.context['view'].request.user.pk
        mailboxes = fields['mailboxes'].queryset
        fields['mailboxes'].queryset = mailboxes.filter(account=account)
        # TODO do it on permissions or in self.filter_by_account_field ?
        domain = fields['domain'].queryset
        fields['domain'].queryset = domain.filter(account=account)
        return fields
    
    def validate(self, attrs):
        if not attrs['mailboxes'] and not attrs['forward']:
            raise serializers.ValidationError("mailboxes or forward addresses should be provided")
        return attrs

