from django.forms import widgets
from django.shortcuts import get_object_or_404
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
    
    def validate(self, attrs):
        attrs = super(SystemUserSerializer, self).validate(attrs)
        user = SystemUser(
            username=attrs.get('username') or self.instance.username,
            shell=attrs.get('shell') or self.instance.shell,
        )
        validate_home(user, attrs, self.get_account())
        return attrs
    
    def validate_groups(self, attrs, source):
        groups = attrs.get(source)
        if groups:
            for group in groups:
                if group.username == attrs['username']:
                    raise serializers.ValidationError(
                        _("Do not make the user member of its group"))
        return attrs
