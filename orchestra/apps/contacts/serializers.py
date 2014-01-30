from rest_framework import serializers

from .models import Contact, Contract


class ContactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Contact


class ContractSerializer(serializers.HyperlinkedModelSerializer):
    service = serializers.RelatedField()
    
    class Meta:
        model = Contract
        fields = ('contact', 'service', 'description', 'register_date', 'cancel_date')
