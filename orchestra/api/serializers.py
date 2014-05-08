from django.forms import widgets
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import serializers

from ..core.validators import validate_password


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, label=_('Password'),
            widget=widgets.PasswordInput, validators=[validate_password])


class MultiSelectField(serializers.ChoiceField):
    widget = widgets.CheckboxSelectMultiple
    
    def field_from_native(self, data, files, field_name, into):
        """ convert multiselect data into comma separated string """
        if field_name in data:
            data = data.copy()
            try:
                # data is a querydict when using forms
                data[field_name] = ','.join(data.getlist(field_name))
            except AttributeError:
                data[field_name] = ','.join(data[field_name])
        return super(MultiSelectField, self).field_from_native(data, files, field_name, into)
    
    def valid_value(self, value):
        """ checks for each item if is a valid value """
        for val in value.split(','):
            valid = super(MultiSelectField, self).valid_value(val)
            if not valid:
                return False
        return True
