from rest_framework import serializers

from orchestra.api import router
from orchestra.utils.db import database_ready

from .models import Resource, ResourceData


class ResourceSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    unit = serializers.ReadOnlyField()
    
    class Meta:
        model = ResourceData
        fields = ('name', 'used', 'allocated', 'unit')
        read_only_fields = ('used',)
    
    def to_internal_value(self, raw_data):
        data = super(ResourceSerializer, self).to_internal_value(raw_data)
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
        try:
            viewset = router.get_viewset(related)
        except KeyError:
            # API viewset not registered
            pass
        else:
            fields = list(viewset.serializer_class.Meta.fields)
            try:
                fields.remove('resources')
            except ValueError:
                pass
            viewset.serializer_class.Meta.fields = fields
    # Create nested serializers on target models
    for ct, resources in Resource.objects.group_by('content_type').items():
        model = ct.model_class()
        try:
            router.insert(model, 'resources', ResourceSerializer, required=False, many=True, source='resource_set')
        except KeyError:
            continue
        # TODO this is a fucking workaround, reimplement this on the proper place
        def validate_resources(self, posted, _resources=resources):
            """ Creates missing resources """
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
            return result
        viewset = router.get_viewset(model)
        viewset.serializer_class.validate_resources = validate_resources
        
        old_options = viewset.options
        def options(self, request, resources=resources):
            """ Provides available resources description """
            metadata = old_options(self, request)
            metadata.data['available_resources'] = [
                {
                    'name': resource.name,
                    'on_demand': resource.on_demand,
                    'default_allocation': resource.default_allocation
                } for resource in resources
            ]
            return metadata
        viewset.options = options

if database_ready():
    insert_resource_serializers()
