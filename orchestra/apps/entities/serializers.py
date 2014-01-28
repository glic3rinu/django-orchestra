from rest_framework import serializers

from .models import Entity, Contract


class EntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Entity


class ContractSerializer(serializers.HyperlinkedModelSerializer):
    service = serializers.RelatedField()
    
    class Meta:
        model = Contract
        fields = ('entity', 'service', 'description', 'register_date', 'cancel_date')
