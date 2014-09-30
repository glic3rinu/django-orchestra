from django.contrib.auth import get_user_model
from django.forms import widgets
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import serializers

from orchestra.apps.accounts.serializers import AccountSerializerMixin
from orchestra.core.validators import validate_password


class UserSerializer(AccountSerializerMixin, serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(max_length=128, label=_('Password'),
            validators=[validate_password], write_only=True, required=False,
            widget=widgets.PasswordInput)
    
    class Meta:
        model = get_user_model()
        fields = (
            'url', 'username', 'password', 'first_name', 'last_name', 'email',
            'is_admin', 'is_active',
        )
    
    def validate_password(self, attrs, source):
        """ POST only password """
        if self.object.pk:
            if 'password' in attrs:
                raise serializers.ValidationError(_("Can not set password"))
        elif 'password' not in attrs:
            raise serializers.ValidationError(_("Password required"))
        return attrs
    
    def save_object(self, obj, **kwargs):
        # FIXME this method will be called when saving nested serializers :(
        if not obj.pk:
            obj.set_password(obj.password)
        super(UserSerializer, self).save_object(obj, **kwargs)
