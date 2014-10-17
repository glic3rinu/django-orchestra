from rest_framework import serializers

from orchestra.api import router
from orchestra.apps.accounts.models import Account
from orchestra.apps.accounts.serializers import AccountSerializerMixin

from .models import Bill, BillLine, BillContact


class BillLineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BillLine



class BillSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    lines = BillLineSerializer(source='billlines')
    
    class Meta:
        model = Bill
        fields = (
            'url', 'number', 'type', 'total', 'is_sent', 'created_on', 'due_on',
            'comments', 'html', 'lines'
        )


class BillContactSerializer(AccountSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = BillContact
        fields = ('name', 'address', 'city', 'zipcode', 'country', 'vat')


router.insert(Account, 'billcontact', BillContactSerializer, required=False)
