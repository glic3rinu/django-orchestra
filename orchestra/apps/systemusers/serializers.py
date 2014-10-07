from django.contrib.auth import get_user_model
from django.forms import widgets
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import serializers

from orchestra.apps.accounts.serializers import AccountSerializerMixin
from orchestra.core.validators import validate_password

from .models import SystemUser


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemUser
        fields = ('username',)
    
    def from_native(self, data, files=None):
        return SystemUser.objects.get(username=data['username'])


class SystemUserSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(max_length=128, label=_('Password'),
            validators=[validate_password], write_only=True, required=False,
            widget=widgets.PasswordInput)
    groups = GroupSerializer(many=True, allow_add_remove=True, required=False)
    
    class Meta:
        model = SystemUser
        fields = (
            'url', 'username', 'password', 'home', 'shell', 'groups', 'is_active',
        )
    
    def validate_password(self, attrs, source):
        """ POST only password """
        if self.object:
            if 'password' in attrs:
                raise serializers.ValidationError(_("Can not set password"))
        elif 'password' not in attrs:
            raise serializers.ValidationError(_("Password required"))
        return attrs
    
    # TODO validate gruops != self
    
    def save_object(self, obj, **kwargs):
        # FIXME this method will be called when saving nested serializers :(
        if not obj.pk:
            obj.set_password(obj.password)
        super(SystemUserSerializer, self).save_object(obj, **kwargs)
