from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.api.serializers import HyperlinkedModelSerializer
from orchestra.contrib.accounts.serializers import AccountSerializerMixin

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
    records = RecordSerializer(required=False, many=True) #allow_add_remove=True)
    
    class Meta:
        model = Domain
        fields = ('url', 'id', 'name', 'records')
        postonly_fields = ('name',)
    
    def clean_name(self, attrs, source):
        """ prevent users creating subdomains of other users domains """
        name = attrs[source]
        parent = Domain.get_parent_domain(name)
        if parent and parent.account != self.account:
            raise ValidationError(_("Can not create subdomains of other users domains"))
        return attrs
    
    def validate(self, data):
        """ Checks if everything is consistent """
        data = super(DomainSerializer, self).validate(data)
        if self.instance and data.get('name'):
            records = data['records']
            domain = domain_for_validation(self.instance, records)
            validators.validate_zone(domain.render_zone())
        return data
