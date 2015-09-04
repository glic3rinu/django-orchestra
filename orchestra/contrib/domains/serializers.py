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
    records = RecordSerializer(required=False, many=True)
    
    class Meta:
        model = Domain
        fields = ('url', 'id', 'name', 'records')
        postonly_fields = ('name',)
    
    def clean_name(self, attrs, source):
        """ prevent users creating subdomains of other users domains """
        name = attrs[source]
        parent = Domain.objects.get_parent(name)
        if parent and parent.account != self.account:
            raise ValidationError(_("Can not create subdomains of other users domains"))
        return attrs
    
    def validate(self, data):
        """ Checks if everything is consistent """
        data = super(DomainSerializer, self).validate(data)
        name = data.get('name')
        if name:
            instance = self.instance
            if instance is None:
                instance = Domain(name=name, account=self.account)
            records = data['records']
            domain = domain_for_validation(instance, records)
            validators.validate_zone(domain.render_zone())
        return data
    
    def create(self, validated_data):
        records = validated_data.pop('records')
        domain = super(DomainSerializer, self).create(validated_data)
        for record in records:
            domain.records.create(type=record['type'], value=record['value'])
        return domain
    
    def update(self, instance, validated_data):
        precords = validated_data.pop('records')
        domain = super(DomainSerializer, self).update(instance, validated_data)
        to_delete = []
        for erecord in domain.records.all():
            match = False
            for ix, precord in enumerate(precords):
                if erecord.type == precord['type'] and erecord.value == precord['value']:
                    match = True
                    break
            if match:
                precords.pop(ix)
            else:
                to_delete.append(erecord)
        for precord in precords:
            try:
                recycled = to_delete.pop()
            except IndexError:
                domain.records.create(type=precord['type'], value=precord['value'])
            else:
                recycled.type = precord['type']
                recycled.value = precord['value']
                recycled.save()
        return domain
