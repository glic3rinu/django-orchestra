from rest_framework import serializers

from orchestra.api import router

from .models import Resource, ResourceAllocation


class ResourceSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    current = serializers.SerializerMethodField('get_current')
    allocation = serializers.IntegerField(source='value')
    
    class Meta:
        model = ResourceAllocation
        fields = ('name', 'current', 'allocation')
    
    def get_name(self, instance):
        return instance.resource.name
    
    def get_current(self, instance):
        return instance.resource.get_current()


for resources in Resource.group_by_content_type():
    model = resources[0].content_type.model_class()
    router.insert(model, 'resources', ResourceSerializer, required=False,
                  source='allocations')
