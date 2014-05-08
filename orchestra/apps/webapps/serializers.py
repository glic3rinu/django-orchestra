from rest_framework import serializers

from orchestra.api.fields import OptionField
from orchestra.apps.accounts.serializers import AccountSerializerMixin

from .models import WebApp


class WebAppSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    options = OptionField(required=False)
    
    class Meta:
        model = WebApp
        fields = ('url', 'name', 'type', 'options')
