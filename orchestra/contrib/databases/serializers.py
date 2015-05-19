from rest_framework import serializers

from orchestra.api.serializers import (HyperlinkedModelSerializer,
    SetPasswordHyperlinkedSerializer, RelatedHyperlinkedModelSerializer)
from orchestra.contrib.accounts.serializers import AccountSerializerMixin

from .models import Database, DatabaseUser


class RelatedDatabaseUserSerializer(AccountSerializerMixin, RelatedHyperlinkedModelSerializer):
    class Meta:
        model = DatabaseUser
        fields = ('url', 'id', 'username')


class DatabaseSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    users = RelatedDatabaseUserSerializer(many=True) #allow_add_remove=True
    
    class Meta:
        model = Database
        fields = ('url', 'id', 'name', 'type', 'users')
        postonly_fields = ('name', 'type')
    
    def validate(self, attrs):
        attrs = super(DatabaseSerializer, self).validate(attrs)
        for user in attrs['users']:
            if user.type != attrs['type']:
                raise serializers.ValidationError("User type must be" % attrs['type'])
        return attrs


class RelatedDatabaseSerializer(AccountSerializerMixin, RelatedHyperlinkedModelSerializer):
    class Meta:
        model = Database
        fields = ('url', 'id', 'name',)


class DatabaseUserSerializer(AccountSerializerMixin, SetPasswordHyperlinkedSerializer):
    databases = RelatedDatabaseSerializer(many=True, required=False) # allow_add_remove=True
    
    class Meta:
        model = DatabaseUser
        fields = ('url', 'id', 'username', 'password', 'type', 'databases')
        postonly_fields = ('username', 'type', 'password')
    
    def validate(self, attrs):
        attrs = super(DatabaseUserSerializer, self).validate(attrs)
        for database in attrs.get('databases', []):
            if database.type != attrs['type']:
                raise serializers.ValidationError("Database type must be" % attrs['type'])
        return attrs
