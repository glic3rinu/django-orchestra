from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = (
            'url', 'id', 'username', 'type', 'language', 'short_name', 'full_name', 'date_joined', 'last_login',
            'is_active'
        )


class AccountSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        super(AccountSerializerMixin, self).__init__(*args, **kwargs)
        self.account = self.get_account()
    
    def get_account(self):
        request = self.context.get('request')
        if request:
            return request.user
    
    def create(self, validated_data):
        validated_data['account'] = self.get_account()
        return super(AccountSerializerMixin, self).create(validated_data)
