from django.core.exceptions import ValidationError
from rest_framework import serializers

from orchestra.api.serializers import HyperlinkedModelSerializer, RelatedHyperlinkedModelSerializer
from orchestra.contrib.accounts.serializers import AccountSerializerMixin

from .directives import SiteDirective
from .models import Website, Content, WebsiteDirective
from .utils import normurlpath
from .validators import validate_domain_protocol



class RelatedDomainSerializer(AccountSerializerMixin, RelatedHyperlinkedModelSerializer):
    class Meta:
        model = Website.domains.field.rel.to
        fields = ('url', 'id', 'name')


class RelatedWebAppSerializer(AccountSerializerMixin, RelatedHyperlinkedModelSerializer):
    class Meta:
        model = Content.webapp.field.rel.to
        fields = ('url', 'id', 'name', 'type')


class ContentSerializer(serializers.ModelSerializer):
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
    domains = RelatedDomainSerializer(many=True, required=False)
    contents = ContentSerializer(required=False, many=True, source='content_set')
    directives = DirectiveSerializer(required=False)
    
    class Meta:
        model = Website
        fields = ('url', 'id', 'name', 'protocol', 'domains', 'is_active', 'contents', 'directives')
        postonly_fields = ('name',)
    
    def validate(self, data):
        """ Prevent multiples domains on the same protocol """
        # Validate location and directive uniqueness
        errors = []
        directives = data.get('directives', [])
        if directives:
            locations = set()
            for content in data.get('content_set', []):
                location = content.get('path')
                if location is not None:
                    locations.add(normurlpath(location))
            values = defaultdict(list)
            for name, value in directives.items():
                directive = {
                    'name': name,
                    'value': value,
                }
                try:
                    SiteDirective.get(name).validate_uniqueness(directive, values, locations)
                except ValidationError as err:
                    errors.append(err)
        # Validate domain protocol uniqueness
        instance = self.instance
        for domain in data['domains']:
            try:
                validate_domain_protocol(instance, domain, data['protocol'])
            except ValidationError as err:
                errors.append(err)
        if errors:
            raise ValidationError(errors)
        return data
    
    def create(self, validated_data):
        directives_data = validated_data.pop('directives')
        webapp = super(WebsiteSerializer, self).create(validated_data)
        for key, value in directives_data.items():
            WebsiteDirective.objects.create(webapp=webapp, name=key, value=value)
        return webap
    
    def update_directives(self, instance, directives_data):
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
    
    def update_contents(self, instance, contents_data):
        raise NotImplementedError
    
    def update_domains(self, instance, domains_data):
        raise NotImplementedError
    
    def update(self, instance, validated_data):
        directives_data = validated_data.pop('directives')
        domains_data = validated_data.pop('domains')
        contents_data = validated_data.pop('content_set')
        instance = super(WebsiteSerializer, self).update(instance, validated_data)
        self.update_directives(instance, directives_data)
        self.update_contents(instance, contents_data)
        self.update_domains(instance, domains_data)
        return instance
