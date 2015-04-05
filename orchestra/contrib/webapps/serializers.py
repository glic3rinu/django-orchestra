from orchestra.api.fields import OptionField
from orchestra.api.serializers import HyperlinkedModelSerializer
from orchestra.contrib.accounts.serializers import AccountSerializerMixin

from .models import WebApp


class WebAppSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    options = OptionField(required=False)
    
    class Meta:
        model = WebApp
        fields = ('url', 'name', 'type', 'options')
        postonly_fields = ('name', 'type')
