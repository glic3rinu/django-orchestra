from rest_framework import serializers

from orchestra.apps.accounts.serializers import AccountSerializerMixin

from .models import Bill, BillLine


class BillLineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BillLine



class BillSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    lines = BillLineSerializer(source='billlines')
    
    class Meta:
        model = Bill
        fields = (
            'url', 'ident', 'bill_type', 'status', 'created_on', 'due_on',
            'comments', 'html', 'lines'
        )
