from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
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
    
    def clean_name(self, attrs, source):
        """ prevent users creating subdomains of other users domains """
        name = attrs[source]
        top = Domain.get_parent_domain(name)
        if top and top.account != self.account:
            raise ValidationError(_("Can not create subdomains of other users domains"))
        return attrs
    
    def full_clean(self, instance):
        """ Checks if everything is consistent """
        instance = super(DomainSerializer, self).full_clean(instance)
        if instance and instance.name:
            records = self.init_data.get('records', [])
            domain = domain_for_validation(instance, records)
            validators.validate_zone(domain.render_zone())
        return instance
