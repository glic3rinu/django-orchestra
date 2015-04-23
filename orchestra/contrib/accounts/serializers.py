from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = (
            'url', 'username', 'type', 'language', 'short_name', 'full_name', 'date_joined',
            'is_active'
        )


class AccountSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        super(AccountSerializerMixin, self).__init__(*args, **kwargs)
        self.account = None
        request = self.context.get('request')
        if request:
            self.account = request.user
    
    def create(self, validated_data):
        validated_data['account'] = self.account
        return super(AccountSerializerMixin, self).create(validated_data)
