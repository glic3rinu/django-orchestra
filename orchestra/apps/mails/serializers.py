from rest_framework import serializers

from orchestra.apps.accounts.serializers import AccountSerializerMixin

from .models import Mailbox, Address


class MailboxSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mailbox
        fields = ('url', 'name', 'use_custom_filtering', 'custom_filtering', 'addresses')


class AddressSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address
        fields = ('url', 'name', 'domain', 'mailboxes', 'forward')
    
    def get_fields(self, *args, **kwargs):
        fields = super(AddressSerializer, self).get_fields(*args, **kwargs)
        account = self.context['view'].request.user.account_id
        mailboxes = fields['mailboxes'].queryset
        fields['mailboxes'].queryset = mailboxes.filter(account=account)
        # TODO do it on permissions or in self.filter_by_account_field ?
        domain = fields['domain'].queryset
        fields['domain'].queryset = domain  .filter(account=account)
        return fields
