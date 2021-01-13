from django.db import models
from rest_framework import serializers

from orchestra.api.serializers import HyperlinkedModelSerializer
from orchestra.contrib.accounts.serializers import AccountSerializerMixin

from .models import WebApp, WebAppOption


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebAppOption
        fields = ('name', 'value')
    
    def to_representation(self, instance):
        return {prop.name: prop.value for prop in instance.all()}
    
    def to_internal_value(self, data):
        return data


class DataField(serializers.Field):
    def to_representation(self, data):
        return data


class WebAppSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    options = OptionSerializer(required=False)
    data = DataField()
    
    class Meta:
        model = WebApp
        fields = ('url', 'id', 'name', 'type', 'options', 'data',)
        postonly_fields = ('name', 'type')
    
    def __init__(self, *args, **kwargs):
        super(WebAppSerializer, self).__init__(*args, **kwargs)
        if isinstance(self.instance, models.Model):
            type_serializer = self.instance.type_instance.serializer
            if type_serializer:
                self.fields['data'] = type_serializer()
    
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        webapp = super(WebAppSerializer, self).create(validated_data)
        for key, value in options_data.items():
            WebAppOption.objects.create(webapp=webapp, name=key, value=value)
        return webap
    
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options')
        instance = super(WebAppSerializer, self).update(instance, validated_data)
        existing = {}
        for obj in instance.options.all():
            existing[obj.name] = obj
        posted = set()
        for key, value in options_data.items():
            posted.add(key)
            try:
                option = existing[key]
            except KeyError:
                option = instance.options.create(name=key, value=value)
            else:
                if option.value != value:
                    option.value = value
                    option.save(update_fields=('value',))
        for to_delete in set(existing.keys())-posted:
            existing[to_delete].delete()
        return instance
