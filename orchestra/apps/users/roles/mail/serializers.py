from rest_framework import serializers

from orchestra.api import router
from orchestra.apps.accounts.serializers import AccountSerializerMixin

from .models import Address, Mailbox


#class AddressSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = Address
#        fields = ('url', 'name', 'domain', 'destination')


class NestedMailboxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mailbox
        fields = ('url', 'use_custom_filtering', 'custom_filtering')


class MailboxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mailbox
        fields = ('url', 'user', 'use_custom_filtering', 'custom_filtering')


class AddressSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address
        fields = ('url', 'name', 'domain', 'mailboxes', 'forward')
    
    def get_fields(self, *args, **kwargs):
        fields = super(AddressSerializer, self).get_fields(*args, **kwargs)
        account = self.context['view'].request.user.account_id
        mailboxes = fields['mailboxes'].queryset.select_related('user')
        fields['mailboxes'].queryset = mailboxes.filter(user__account=account)
        # TODO do it on permissions or in self.filter_by_account_field ?
        domain = fields['domain'].queryset
        fields['domain'].queryset = domain  .filter(account=account)
        return fields


router.insert('users', 'mailbox', NestedMailboxSerializer, required=False)
