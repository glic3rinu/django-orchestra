from rest_framework import serializers

from orchestra.apps.accounts.serializers import AccountSerializerMixin

from .models import List


class ListSerializer(AccountSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ('name', 'address_name', 'address_domain',)
