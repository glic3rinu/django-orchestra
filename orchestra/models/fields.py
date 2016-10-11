import os

from django.core import exceptions
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.fields.files import FileField, FieldFile
from django.utils.text import capfirst

from ..forms.fields import MultiSelectFormField


class MultiSelectField(models.CharField):
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
        else:
            return ','.join(value)
    
    def to_python(self, value):
        if value:
            if isinstance(value, str):
                return value.split(',')
            return value
        return []
    
    def from_db_value(self, value, expression, connection, context):
        if value:
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
        if self.choices:
            arr_choices = self.get_choices_selected(self.get_choices())
            for opt_select in value:
                if (opt_select not in arr_choices):
                    msg = self.error_messages['invalid_choice'] % {'value': opt_select}
                    raise exceptions.ValidationError(msg)
    
    def get_choices_selected(self, arr_choices=''):
        if not arr_choices:
            return False
        return [value for value, __ in arr_choices]


class NullableCharField(models.CharField):
     def get_db_prep_value(self, value, connection=None, prepared=False):
         return value or None


class PrivateFieldFile(FieldFile):
    @property
    def url(self):
        self._require_file()
        app_label = self.instance._meta.app_label
        model_name  = self.instance._meta.object_name.lower()
        field_name = self.field.name
        pk = self.instance.pk
        filename = os.path.basename(self.path)
        args = [app_label, model_name, field_name, pk, filename]
        return reverse('private-media', args=args)
    
    @property
    def condition(self):
        return self.field.condition
    
    @property
    def attachment(self):
        return self.field.attachment


class PrivateFileField(FileField):
    attr_class = PrivateFieldFile
    
    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, attachment=True,
                 condition=lambda request, instance: request.user.is_superuser, **kwargs):
        super(PrivateFileField, self).__init__(verbose_name, name, upload_to, storage, **kwargs)
        self.condition = condition
        self.attachment = attachment
