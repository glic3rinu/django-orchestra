from django.core import exceptions
from django.db import models
from django.utils.text import capfirst

from ..forms.fields import MultiSelectFormField
from ..utils.apps import isinstalled


class MultiSelectField(models.CharField, metaclass=models.SubfieldBase):
    def formfield(self, **kwargs):
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'choices': self.choices
        }
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)
    
    def get_db_prep_value(self, value, connection=None, prepared=False):
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            return ','.join(value)
    
    def to_python(self, value):
        if value:
#            if isinstance(value, tuple) and value[0].startswith('('):
#                # Workaround unknown bug on default model values
#                # [u"('SUPPORT'", u" 'ADMIN'", u" 'BILLING'", u" 'TECH'", u" 'ADDS'", u" 'EMERGENCY')"]
#                value = list(eval(', '.join(value)))
            if isinstance(value, str):
                return value.split(',')
            return value
        return []
    
    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            def func(self, field=name, choices=dict(self.choices)):
                return ','.join([choices.get(value, value) for value in getattr(self, field)])
            setattr(cls, 'get_%s_display' % self.name, func)
    
    def validate(self, value, model_instance):
        arr_choices = self.get_choices_selected(self.get_choices_default())
        for opt_select in value:
            if (opt_select not in arr_choices):
                msg = self.error_messages['invalid_choice'] % value
                raise exceptions.ValidationError(msg)
        return
    
    def get_choices_selected(self, arr_choices=''):
        if not arr_choices:
            return False
        return [ value for value,__ in arr_choices ]


class NullableCharField(models.CharField):
     def get_db_prep_value(self, value, connection=None, prepared=False):
         return value or None


if isinstalled('south'):
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^orchestra\.models\.fields\.MultiSelectField"])
    add_introspection_rules([], ["^orchestra\.models\.fields\.NullableCharField"])
