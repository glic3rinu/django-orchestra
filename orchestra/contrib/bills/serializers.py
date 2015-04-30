from rest_framework import serializers

from orchestra.api import router
from orchestra.contrib.accounts.models import Account
from orchestra.contrib.accounts.serializers import AccountSerializerMixin

from .models import Bill, BillLine, BillContact


class BillLineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BillLine



class BillSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
#    lines = BillLineSerializer(source='lines')
    
    class Meta:
        model = Bill
        fields = (
            'url', 'id', 'number', 'type', 'total', 'is_sent', 'created_on', 'due_on',
            'comments',
#             'lines'
        )


class BillContactSerializer(AccountSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = BillContact
        fields = ('name', 'address', 'city', 'zipcode', 'country', 'vat')


router.insert(Account, 'billcontact', BillContactSerializer, required=False)
