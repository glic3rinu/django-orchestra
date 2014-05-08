from rest_framework import serializers

from orchestra.api.fields import OptionField
from orchestra.apps.accounts.serializers import AccountSerializerMixin

from .models import Website, Content


class ContentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Content
        fields = ('webapp', 'path')


class WebsiteSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    contents = ContentSerializer(required=False, many=True, allow_add_remove=True,
            source='content_set')
    options = OptionField(required=False)
    
    class Meta:
        model = Website
        fields = ('url', 'name', 'port', 'domains', 'is_active', 'contents', 'options')
