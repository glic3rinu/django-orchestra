import re
from collections import OrderedDict

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.functional import Promise

from orchestra.core import validators
from orchestra.utils.python import import_class, format_exception


default_app_config = 'orchestra.contrib.settings.apps.SettingsConfig'


class Setting(object):
    """
    Keeps track of the defined settings and provides extra batteries like value validation.
    """
    conf_settings = settings
    settings = OrderedDict()
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        value = str(self.value)
        value = ("'%s'" if isinstance(value, str) else '%s') % value
        return '<%s: %s>' % (self.name, value)
    
    def __new__(cls, name, default, help_text="", choices=None, editable=True, serializable=True,
                multiple=False, validators=[], types=[], call_init=False):
        if call_init:
            return super(Setting, cls).__new__(cls)
        cls.settings[name] = cls(name, default, help_text=help_text, choices=choices, editable=editable,
            serializable=serializable, multiple=multiple, validators=validators, types=types, call_init=True)
        return cls.get_value(name, default)
    
    def __init__(self, *args, **kwargs):
        self.name, self.default = args
        for name, value in kwargs.items():
            setattr(self, name, value)
        self.value = self.get_value(self.name, self.default)
        self.settings[name] = self
    
    @classmethod
    def validate_choices(cls, value):
        if not isinstance(value, (list, tuple)):
            raise ValidationError("%s is not a valid choices." % value)
        for choice in value:
            if not isinstance(choice, (list, tuple)) or len(choice) != 2:
                raise ValidationError("%s is not a valid choice." % choice)
            value, verbose = choice
            if not isinstance(verbose, (str, Promise)):
                raise ValidationError("%s is not a valid verbose name." % value)
    
    @classmethod
    def validate_import_class(cls, value):
        try:
            import_class(value)
        except Exception as exc:
            raise ValidationError(format_exception(exc))
    
    @classmethod
    def validate_model_label(cls, value):
        from django.apps import apps
        try:
            apps.get_model(*value.split('.'))
        except Exception as exc:
            raise ValidationError(format_exception(exc))
    
    @classmethod
    def string_format_validator(cls, names, modulo=True):
        def validate_string_format(value, names=names, modulo=modulo):
            errors = []
            regex = r'%\(([^\)]+)\)' if modulo else r'{([^}]+)}'
            for n in re.findall(regex, value):
                if n not in names:
                    errors.append(
                        ValidationError('%s is not a valid format name.' % n)
                    )
            if errors:
                raise ValidationError(errors)
        return validate_string_format
    
    def validate_value(self, value):
        if value:
            validators.all_valid(value, self.validators)
        valid_types = list(self.types)
        if self.choices:
            choices = self.choices
            if callable(choices):
                choices = choices()
            choices = [n for n,v in choices]
            values = value
            if not isinstance(values, (list, tuple)):
                values = [value]
            for cvalue in values:
                if cvalue not in choices:
                    raise ValidationError("'%s' not in '%s'" % (value, ', '.join(choices)))
        if isinstance(self.default, (list, tuple)):
            valid_types.extend([list, tuple])
        valid_types.append(type(self.default))
        if not isinstance(value, tuple(valid_types)):
            raise ValidationError("%s is not a valid type (%s)." %
                (type(value).__name__, ', '.join(t.__name__ for t in valid_types))
            )
    
    def validate(self):
        self.validate_value(self.value)
    
    @classmethod
    def get_value(cls, name, default):
        return getattr(cls.conf_settings, name, default)
