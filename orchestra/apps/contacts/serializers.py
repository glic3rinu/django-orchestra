from rest_framework import serializers

from orchestra.api.serializers import MultiSelectField
from orchestra.apps.accounts.serializers import AccountSerializerMixin

from .models import Contact, InvoiceContact


class ContactSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    email_usage = MultiSelectField(choices=Contact.EMAIL_USAGES)
    class Meta:
        model = Contact
        fields = (
            'url', 'short_name', 'full_name', 'email', 'email_usage', 'phone',
            'phone2', 'address', 'city', 'zipcode', 'country'
        )


class InvoiceContactSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InvoiceContact
        fields = ('url', 'name', 'address', 'city', 'zipcode', 'country', 'vat')
