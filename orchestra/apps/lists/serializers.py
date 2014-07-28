from rest_framework import serializers

from orchestra.apps.accounts.serializers import AccountSerializerMixin

from .models import List


class ListSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = List
        fields = ('url', 'name', 'address_name', 'address_domain')
