from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from orchestra.api.fields import OptionField
from orchestra.api.serializers import HyperlinkedModelSerializer
from orchestra.apps.accounts.serializers import AccountSerializerMixin

from .models import Website, Content


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


class WebsiteSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    domains = RelatedDomainSerializer(many=True, allow_add_remove=True, required=False)
    contents = ContentSerializer(required=False, many=True, allow_add_remove=True,
            source='contents')
    options = OptionField(required=False)
    
    class Meta:
        model = Website
        fields = ('url', 'name', 'port', 'domains', 'is_active', 'contents', 'options')
        postonly_fileds = ('name',)
    
    def full_clean(self, instance):
        """ Prevent multiples domains on the same port """
        existing = []
        for domain in instance._m2m_data['domains']:
            if domain.websites.filter(port=instance.port).exclude(pk=instance.pk).exists():
                existing.append(domain.name)
        if existing:
            context = (', '.join(existing), instance.port)
            raise ValidationError({
                'domains': 'A website is already defined for "%s" on port %s' % context
            })
        return instance

