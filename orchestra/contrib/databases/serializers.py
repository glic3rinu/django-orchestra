from django.forms import widgets
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.api.serializers import HyperlinkedModelSerializer, SetPasswordHyperlinkedSerializer
from orchestra.contrib.accounts.serializers import AccountSerializerMixin

from .models import Database, DatabaseUser


class RelatedDatabaseUserSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DatabaseUser
        fields = ('url', 'username')
    
    def from_native(self, data, files=None):
        queryset = self.opts.model.objects.filter(account=self.account)
        return get_object_or_404(queryset, username=data['username'])


class DatabaseSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    users = RelatedDatabaseUserSerializer(many=True) #allow_add_remove=True
    
    class Meta:
        model = Database
        fields = ('url', 'name', 'type', 'users')
        postonly_fields = ('name', 'type')
    
    def validate(self, attrs):
        attrs = super(DatabaseSerializer, self).validate(attrs)
        for user in attrs['users']:
            if user.type != attrs['type']:
                raise serializers.ValidationError("User type must be" % attrs['type'])
        return attrs


class RelatedDatabaseSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Database
        fields = ('url', 'name',)
    
    def from_native(self, data, files=None):
        queryset = self.opts.model.objects.filter(account=self.account)
        return get_object_or_404(queryset, name=data['name'])


class DatabaseUserSerializer(AccountSerializerMixin, SetPasswordHyperlinkedSerializer):
    databases = RelatedDatabaseSerializer(many=True, required=False) # allow_add_remove=True
    
    class Meta:
        model = DatabaseUser
        fields = ('url', 'username', 'password', 'type', 'databases')
        postonly_fields = ('username', 'type', 'password')
    
    def validate(self, attrs):
        attrs = super(DatabaseUserSerializer, self).validate(attrs)
        for database in attrs.get('databases', []):
            if database.type != attrs['type']:
                raise serializers.ValidationError("Database type must be" % attrs['type'])
        return attrs
