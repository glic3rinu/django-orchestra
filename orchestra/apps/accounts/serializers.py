from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = (
            'url', 'username', 'type', 'language', 'date_joined', 'is_active'
        )


class AccountSerializerMixin(object):
    def __init__(self, *args, **kwargs):
        super(AccountSerializerMixin, self).__init__(*args, **kwargs)
        self.account = None
        request = self.context.get('request')
        if request:
            self.account = request.user
    
    def save_object(self, obj, **kwargs):
        obj.account = self.account
        super(AccountSerializerMixin, self).save_object(obj, **kwargs)
