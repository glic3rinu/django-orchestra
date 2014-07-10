from rest_framework import serializers

from orchestra.api import router
from orchestra.utils import running_syncdb

from .models import Resource, ResourceData


class ResourceSerializer(serializers.ModelSerializer):
    # TODO required allocation serializers (like resource form)
    # TODO create missing ResourceData (like resource form)
    # TODO make default allocation available on OPTIONS (like resource form)
    name = serializers.SerializerMethodField('get_name')
    
    class Meta:
        model = ResourceData
        fields = ('name', 'used', 'allocated')
        read_only_fields = ('used',)
    
    def get_name(self, instance):
        return instance.resource.name


if not running_syncdb():
    for resources in Resource.group_by_content_type():
        model = resources[0].content_type.model_class()
        router.insert(model, 'resources', ResourceSerializer, required=False)
