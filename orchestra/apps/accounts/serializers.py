from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = (
            'url', 'username', 'type', 'language', 'date_joined', 'is_active'
        )


class AccountSerializerMixin(object):
    def save_object(self, obj, **kwargs):
        obj.account = self.context['request'].user
        super(AccountSerializerMixin, self).save_object(obj, **kwargs)
