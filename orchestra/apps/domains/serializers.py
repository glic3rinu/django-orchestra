from django.core.exceptions import ValidationError
from rest_framework import serializers

from orchestra.api.serializers import HyperlinkedModelSerializer
from orchestra.apps.accounts.serializers import AccountSerializerMixin

from .helpers import domain_for_validation
from .models import Domain, Record
from . import validators


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ('type', 'value')
    
    def get_identity(self, data):
        return data.get('value')


class DomainSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    """ Validates if this zone generates a correct zone file """
    records = RecordSerializer(required=False, many=True, allow_add_remove=True)
    
    class Meta:
        model = Domain
        fields = ('url', 'name', 'records')
        postonly_fields = ('name',)
    
    def full_clean(self, instance):
        """ Checks if everything is consistent """
        instance = super(DomainSerializer, self).full_clean(instance)
        if instance and instance.name:
            records = self.init_data['records']
            domain = domain_for_validation(instance, records)
            try:
                validators.validate_zone(domain.render_zone())
            except ValidationError as err:
                self._errors = {
                    'all': err.message
                }
                return None
        return instance
