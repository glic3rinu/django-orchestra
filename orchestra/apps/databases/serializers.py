from django.forms import widgets
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import serializers

from orchestra.api.serializers import HyperlinkedModelSerializer
from orchestra.apps.accounts.serializers import AccountSerializerMixin
from orchestra.core.validators import validate_password

from .models import Database, DatabaseUser


class RelatedDatabaseUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DatabaseUser
        fields = ('url', 'username')
    
    def from_native(self, data, files=None):
        return DatabaseUser.objects.get(username=data['username'])


class DatabaseSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    users = RelatedDatabaseUserSerializer(many=True, allow_add_remove=True)
    # TODO clean user.type = db.type
    
    class Meta:
        model = Database
        fields = ('url', 'name', 'type', 'users')
        postonly_fields = ('name', 'type')


class RelatedDatabaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Database
        fields = ('url', 'name',)
    
    def from_native(self, data, files=None):
        return Database.objects.get(name=data['name'])


class DatabaseUserSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    password = serializers.CharField(max_length=128, label=_('Password'),
            validators=[validate_password], write_only=True,
            widget=widgets.PasswordInput)
    databases = RelatedDatabaseSerializer(many=True, allow_add_remove=True, required=False)
    # TODO clean user.type = db.type
        
    class Meta:
        model = DatabaseUser
        fields = ('url', 'username', 'password', 'type', 'databases')
        postonly_fields = ('username', 'type')
    
    def save_object(self, obj, **kwargs):
        # FIXME this method will be called when saving nested serializers :(
        if not obj.pk:
            obj.set_password(obj.password)
        super(DatabaseUserSerializer, self).save_object(obj, **kwargs)
