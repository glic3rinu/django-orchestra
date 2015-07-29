from rest_framework import serializers

from orchestra.contrib.accounts.serializers import AccountSerializerMixin

from .methods import PaymentMethod
from .models import PaymentSource, Transaction


class PaymentSourceSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PaymentSource
        fields = ('url', 'id', 'method', 'data', 'is_active')
    
    def validate(self, data):
        """ validate data according to method """
        data = super(PaymentSourceSerializer, self).validate(data)
        plugin = PaymentMethod.get(data['method'])
        serializer_class = plugin().get_serializer()
        serializer = serializer_class(data=data['data'])
        if not serializer.is_valid():
            raise serializers.ValidationError(serializer.errors)
        return data
    
    def transform_data(self, obj, value):
        if not obj:
            return {}
        if obj.method:
            plugin = PaymentMethod.get(obj.method)
            serializer_class = plugin().get_serializer()
            return serializer_class().to_native(obj.data)
        return obj.data
    
    # TODO
    def metadata(self):
        meta = super(PaymentSourceSerializer, self).metadata()
        meta['data'] = {
            method.get_name(): method().get_serializer()().metadata()
                for method in PaymentMethod.get_plugins()
        }
        return meta


class TransactionSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
