from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = (
            'url', 'username', 'type', 'language', 'register_date', 'is_active'
        )


class AccountSerializerMixin(object):
    def save_object(self, obj, **kwargs):
        obj.account = self.context['request'].user.account
        super(AccountSerializerMixin, self).save_object(obj, **kwargs)
