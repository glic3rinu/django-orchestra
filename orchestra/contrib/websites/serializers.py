from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from orchestra.api.serializers import HyperlinkedModelSerializer
from orchestra.contrib.accounts.serializers import AccountSerializerMixin

from .models import Website, Content, WebsiteDirective
from .validators import validate_domain_protocol


class RelatedDomainSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Website.domains.field.rel.to
        fields = ('url', 'name')
    
    def from_native(self, data, files=None):
        queryset = self.opts.model.objects.filter(account=self.account)
        return get_object_or_404(queryset, name=data['name'])


class RelatedWebAppSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Content.webapp.field.rel.to
        fields = ('url', 'name', 'type')
    
    def from_native(self, data, files=None):
        queryset = self.opts.model.objects.filter(account=self.account)
        return get_object_or_404(queryset, name=data['name'])


class ContentSerializer(serializers.HyperlinkedModelSerializer):
    webapp = RelatedWebAppSerializer()
    
    class Meta:
        model = Content
        fields = ('webapp', 'path')
    
    def get_identity(self, data):
        return '%s-%s' % (data.get('website'), data.get('path'))


class DirectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteDirective
        fields = ('name', 'value')
    
    def to_representation(self, instance):
        return {prop.name: prop.value for prop in instance.all()}
    
    def to_internal_value(self, data):
        return data


class WebsiteSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    domains = RelatedDomainSerializer(many=True, required=False) #allow_add_remove=True
    contents = ContentSerializer(required=False, many=True, #allow_add_remove=True,
            source='content_set')
    directives = DirectiveSerializer(required=False)
    
    class Meta:
        model = Website
        fields = ('url', 'name', 'protocol', 'domains', 'is_active', 'contents', 'directives')
        postonly_fileds = ('name',)
    
    def full_clean(self, instance):
        """ Prevent multiples domains on the same protocol """
        for domain in instance._m2m_data['domains']:
            try:
                validate_domain_protocol(instance, domain, instance.protocol)
            except ValidationError as e:
                # TODO not sure about this one
                self.add_error(None, e)
        return instance
    
    def create(self, validated_data):
        directives_data = validated_data.pop('directives')
        webapp = super(WebsiteSerializer, self).create(validated_data)
        for key, value in directives_data.items():
            WebsiteDirective.objects.create(webapp=webapp, name=key, value=value)
        return webap
    
    def update(self, instance, validated_data):
        directives_data = validated_data.pop('directives')
        instance = super(WebsiteSerializer, self).update(instance, validated_data)
        existing = {}
        for obj in instance.directives.all():
            existing[obj.name] = obj
        posted = set()
        for key, value in directives_data.items():
            posted.add(key)
            try:
                directive = existing[key]
            except KeyError:
                directive = instance.directives.create(name=key, value=value)
            else:
                if directive.value != value:
                    directive.value = value
                    directive.save(update_fields=('value',))
        for to_delete in set(existing.keys())-posted:
            existing[to_delete].delete()
        return instance
