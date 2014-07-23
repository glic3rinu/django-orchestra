from rest_framework import serializers

from .models import Bill, BillLine


class BillLineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BillLine


class BillSerializer(serializers.HyperlinkedModelSerializer):
    lines = BillLineSerializer(source='billlines')
    
    class Meta:
        model = Bill
