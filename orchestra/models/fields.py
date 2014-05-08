from django.db import models
from django.utils.text import capfirst

from ..forms.fields import MultiSelectFormField
from ..utils.apps import isinstalled


class MultiSelectField(models.CharField):
    __metaclass__ = models.SubfieldBase
    
    def formfield(self, **kwargs):
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
            'choices': self.choices
        }
        if self.has_default():
            defaults['initial'] = eval(self.get_default())
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)
    
    def get_db_prep_value(self, value, connection=None, prepared=False):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ','.join(value)
    
    def to_python(self, value):
        if value is not None:
            return value if isinstance(value, list) else value.split(',')
        return ''
    
    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            def func(self, field=name, choices=dict(self.choices)):
                ','.join([ choices.get(value, value) for value in getattr(self, field) ])
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


if isinstalled('south'):
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^controller\.models\.fields\.MultiSelectField"])
