from rest_framework import serializers

#from orchestra.api.serializers import MultiSelectField
from orchestra.contrib.accounts.serializers import AccountSerializerMixin

from .models import Contact


class ContactSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    email_usage = serializers.MultipleChoiceField(choices=Contact.EMAIL_USAGES)
    
    class Meta:
        model = Contact
        fields = (
            'url', 'id', 'short_name', 'full_name', 'email', 'email_usage', 'phone',
            'phone2', 'address', 'city', 'zipcode', 'country'
        )
