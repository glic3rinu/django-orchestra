from rest_framework import serializers

from .models import Zone, Record


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ('name', 'type', 'value')


class ZoneSerializer(serializers.HyperlinkedModelSerializer):
    records = RecordSerializer(required=False, many=True, allow_add_remove=True)
    
    class Meta:
        model = Zone
