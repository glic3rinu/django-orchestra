from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.api.serializers import SetPasswordHyperlinkedSerializer, RelatedHyperlinkedModelSerializer
from orchestra.contrib.accounts.serializers import AccountSerializerMixin

from .models import SystemUser
from .validators import validate_home


class RelatedGroupSerializer(AccountSerializerMixin, RelatedHyperlinkedModelSerializer):
    class Meta:
        model = SystemUser
        fields = ('url', 'id', 'username',)


class SystemUserSerializer(AccountSerializerMixin, SetPasswordHyperlinkedSerializer):
    groups = RelatedGroupSerializer(many=True, required=False)
    
    class Meta:
        model = SystemUser
        fields = (
            'url', 'id', 'username', 'password', 'home', 'directory', 'shell', 'groups', 'is_active',
        )
        postonly_fields = ('username', 'password')
    
    def validate_directory(self, directory):
        return directory.lstrip('/')
    
    def validate(self, data):
        data = super(SystemUserSerializer, self).validate(data)
        user = SystemUser(
            username=data.get('username') or self.instance.username,
            shell=data.get('shell') or self.instance.shell,
        )
        validate_home(user, data, self.get_account())
        groups = data.get('groups')
        if groups:
            for group in groups:
                if group.username == data['username']:
                    raise serializers.ValidationError(
                        _("Do not make the user member of its group"))
        return data
