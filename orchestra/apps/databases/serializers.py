from django.forms import widgets
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import serializers

from orchestra.apps.accounts.serializers import AccountSerializerMixin
from orchestra.core.validators import validate_password

from .models import Database, DatabaseUser, Role


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('user', 'is_owner',)


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('database', 'is_owner',)


class DatabaseSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    users = UserSerializer(source='roles', many=True)
    
    class Meta:
        model = Database
        fields = ('url', 'name', 'type', 'users')


class DatabaseUserSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(max_length=128, label=_('Password'),
            validators=[validate_password], write_only=True,
            widget=widgets.PasswordInput)
    roles = RoleSerializer(many=True, read_only=True)
    
    class Meta:
        model = DatabaseUser
        fields = ('url', 'username', 'password', 'type', 'roles')
        write_only_fields = ('username',)
