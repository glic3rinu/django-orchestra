from django.forms import widgets
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import serializers

from ..core.validators import validate_password


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, label=_('Password'),
            widget=widgets.PasswordInput, validators=[validate_password])


class HyperlinkedModelSerializerOptions(serializers.HyperlinkedModelSerializerOptions):
    def __init__(self, meta):
        super(HyperlinkedModelSerializerOptions, self).__init__(meta)
        self.postonly_fields = getattr(meta, 'postonly_fields', ())


class HyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    """ support for postonly_fields, fields whose value can only be set on post """
    _options_class = HyperlinkedModelSerializerOptions
    
    def restore_object(self, attrs, instance=None):
        """ removes postonly_fields from attrs when not posting """
        model_attrs = dict(**attrs)
        if instance is not None:
            for attr, value in attrs.iteritems():
                if attr in self.opts.postonly_fields:
                    model_attrs.pop(attr)
        return super(HyperlinkedModelSerializer, self).restore_object(model_attrs, instance)


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
