from django.forms import widgets
from django.utils.translation import ugettext, ugettext_lazy as _
from rest_framework import serializers

from ..core.validators import validate_password


class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, label=_('Password'),
            widget=widgets.PasswordInput, validators=[validate_password])



from rest_framework.serializers import (HyperlinkedModelSerializerOptions,
                                        HyperlinkedModelSerializer)
 
 
class tHyperlinkedModelSerializerOptions(serializers.HyperlinkedModelSerializerOptions):
    """ Options for PostHyperlinkedModelSerializer """
    
    def __init__(self, meta):
        super(HyperlinkedModelSerializerOptions, self).__init__(meta)
        self.postonly_fields = getattr(meta, 'postonly_fields', ())


class HyperlinkedModelSerializer(HyperlinkedModelSerializer):
    _options_class = HyperlinkedModelSerializerOptions
    
    def to_native(self, obj):
        """ Serialize objects -> primitives. """
        ret = self._dict_class()
        ret.fields = {}
        
        for field_name, field in self.fields.items():
            # Ignore all postonly_fields fron serialization
            if field_name in self.opts.postonly_fields:
                continue
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field
        return ret
    
    def restore_object(self, attrs, instance=None):
        model_attrs, post_attrs = {}, {}
        for attr, value in attrs.iteritems():
            if attr in self.opts.postonly_fields:
                post_attrs[attr] = value
            else:
                model_attrs[attr] = value
        obj = super(HyperlinkedModelSerializer, self).restore_object(model_attrs, instance)
        # Method to process ignored postonly_fields
        self.process_postonly_fields(obj, post_attrs)
        return obj
 
    def process_postonly_fields(self, obj, post_attrs):
        """ Placeholder method for processing data sent in POST. """
        pass


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
