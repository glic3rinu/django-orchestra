from rest_framework import serializers

from .models import PaymentSource, PaymentSource


class PaymentSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PaymentSource


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = PaymentSource
