from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import serializers

from orchestra.api.serializers import HyperlinkedModelSerializer
from orchestra.apps.accounts.serializers import AccountSerializerMixin
from orchestra.core.validators import validate_password

from .models import SystemUser


class GroupSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SystemUser
        fields = ('url', 'username',)
    
    def from_native(self, data, files=None):
        queryset = self.opts.model.objects.filter(account=self.account)
        return get_object_or_404(queryset, username=data['username'])


class SystemUserSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    password = serializers.CharField(max_length=128, label=_('Password'),
            validators=[validate_password], write_only=True, required=False,
            widget=widgets.PasswordInput)
    groups = GroupSerializer(many=True, allow_add_remove=True, required=False)
    
    class Meta:
        model = SystemUser
        fields = (
            'url', 'username', 'password', 'home', 'shell', 'groups', 'is_active',
        )
        postonly_fields = ('username',)
    
    def validate(self, attrs):
        user = SystemUser(
            username=attrs.get('username') or self.object.username,
            shell=attrs.get('shell') or self.object.shell,
        )
        if 'home' in attrs and attrs['home']:
            home = attrs['home'].rstrip('/') + '/'
            if user.has_shell:
                if home != user.get_base_home():
                    raise ValidationError({
                        'home': _("Not a valid home directory.")
                    })
            elif home not in (user.get_home(), self.account.main_systemuser.get_home()):
                raise ValidationError({
                    'home': _("Not a valid home directory.")
                })
        return attrs
    
    def validate_password(self, attrs, source):
        """ POST only password """
        if self.object:
            if 'password' in attrs:
                raise serializers.ValidationError(_("Can not set password"))
        elif 'password' not in attrs:
            raise serializers.ValidationError(_("Password required"))
        return attrs
    
    def validate_groups(self, attrs, source):
        groups = attrs.get(source)
        if groups:
            for group in groups:
                if group.username == attrs['username']:
                    raise serializers.ValidationError(
                        _("Do not make the user member of its group"))
        return attrs
    
    def save_object(self, obj, **kwargs):
        # FIXME this method will be called when saving nested serializers :(
        if not obj.pk:
            obj.set_password(obj.password)
        super(SystemUserSerializer, self).save_object(obj, **kwargs)
