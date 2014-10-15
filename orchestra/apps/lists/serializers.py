from django.forms import widgets
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import serializers

from orchestra.api.serializers import HyperlinkedModelSerializer
from orchestra.apps.accounts.serializers import AccountSerializerMixin
from orchestra.core.validators import validate_password

from .models import List


class ListSerializer(AccountSerializerMixin, HyperlinkedModelSerializer):
    password = serializers.CharField(max_length=128, label=_('Password'),
            validators=[validate_password], write_only=True, required=False,
            widget=widgets.PasswordInput)
    
    class Meta:
        model = List
        fields = ('url', 'name', 'address_name', 'address_domain', 'admin_email')
        postonly_fields = ('name',)
    
    def validate_password(self, attrs, source):
        """ POST only password """
        if self.object:
            if 'password' in attrs:
                raise serializers.ValidationError(_("Can not set password"))
        elif 'password' not in attrs:
            raise serializers.ValidationError(_("Password required"))
        return attrs
    
    def save_object(self, obj, **kwargs):
        if not obj.pk:
            obj.set_password(self.init_data.get('password', ''))
        super(ListSerializer, self).save_object(obj, **kwargs)
