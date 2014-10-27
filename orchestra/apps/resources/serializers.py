from rest_framework import serializers

from orchestra.api import router
from orchestra.utils import database_ready

from .models import Resource, ResourceData


class ResourceSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    unit = serializers.Field()
    
    class Meta:
        model = ResourceData
        fields = ('name', 'used', 'allocated', 'unit')
        read_only_fields = ('used',)
    
    def from_native(self, raw_data, files=None):
        data = super(ResourceSerializer, self).from_native(raw_data, files=files)
        if not data.resource_id:
            data.resource = Resource.objects.get(name=raw_data['name'])
        return data
    
    def get_name(self, instance):
        return instance.resource.name
    
    def get_identity(self, data):
        return data.get('name')


# Monkey-patching section

def insert_resource_serializers():
    # clean previous state
    for related in Resource._related:
        viewset = router.get_viewset(related)
        fields = list(viewset.serializer_class.Meta.fields)
        try:
            fields.remove('resources')
        except ValueError:
            pass
        viewset.serializer_class.Meta.fields = fields
    # Create nested serializers on target models
    for ct, resources in Resource.objects.group_by('content_type').iteritems():
        model = ct.model_class()
        try:
            router.insert(model, 'resources', ResourceSerializer, required=False, many=True, source='resource_set')
        except KeyError:
            continue
        # TODO this is a fucking workaround, reimplement this on the proper place
        def validate_resources(self, attrs, source, _resources=resources):
            """ Creates missing resources """
            posted = attrs.get(source, [])
            result = []
            resources = list(_resources)
            for data in posted:
                resource = data.resource
                if resource not in resources:
                    msg = "Unknown or duplicated resource '%s'." % resource
                    raise serializers.ValidationError(msg)
                resources.remove(resource)
                if not resource.on_demand and not data.allocated:
                    data.allocated = resource.default_allocation
                result.append(data)
            for resource in resources:
                data = ResourceData(resource=resource)
                if not resource.on_demand:
                    data.allocated = resource.default_allocation
                result.append(data)
            attrs[source] = result
            return attrs
        viewset = router.get_viewset(model)
        viewset.serializer_class.validate_resources = validate_resources
        
        old_metadata = viewset.metadata
        def metadata(self, request, resources=resources):
            """ Provides available resources description """
            ret = old_metadata(self, request)
            ret['available_resources'] = [
                {
                    'name': resource.name,
                    'on_demand': resource.on_demand,
                    'default_allocation': resource.default_allocation
                } for resource in resources
            ]
            return ret
        viewset.metadata = metadata

if database_ready():
    insert_resource_serializers()
