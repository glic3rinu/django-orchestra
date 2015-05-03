import re
import sys
from collections import OrderedDict

from django.conf import settings
from django.core.checks import register, Error
from django.core.exceptions import ValidationError, AppRegistryNotReady
from django.core.validators import validate_email
from django.db.models import get_model
from django.utils.functional import Promise
from django.utils.translation import ugettext_lazy as _

from orchestra.utils.python import import_class, format_exception

from .core import validators


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
            raise ValidationError("%s is not a valid choices." % str(value))
        for choice in value:
            if not isinstance(choice, (list, tuple)) or len(choice) != 2:
                raise ValidationError("%s is not a valid choice." % str(choice))
            value, verbose = choice
            if not isinstance(verbose, (str, Promise)):
                raise ValidationError("%s is not a valid verbose name." % value)
    
    @classmethod
    def validate_import_class(cls, value):
        try:
            import_class(value)
        except ImportError as exc:
            if "cannot import name 'settings'" in str(exc):
                # circular dependency on init time
                pass
        except Exception as exc:
            raise ValidationError(format_exception(exc))
    
    @classmethod
    def validate_model_label(cls, value):
        try:
            get_model(*value.split('.'))
        except AppRegistryNotReady:
            # circular dependency on init time
            pass
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
        if isinstance(self.default, (list, tuple)):
            valid_types.extend([list, tuple])
        valid_types.append(type(self.default))
        if not isinstance(value, tuple(valid_types)):
            raise ValidationError("%s is not a valid type (%s)." %
                (type(value).__name__, ', '.join(t.__name__ for t in valid_types))
            )
    
    @classmethod
    def get_value(cls, name, default):
        return getattr(cls.conf_settings, name, default)


@register()
def check_settings(app_configs, **kwargs):
    """ perfroms all the validation """
    messages = []
    for name, setting in Setting.settings.items():
        try:
            setting.validate_value(setting.value)
        except ValidationError as exc:
            msg = "Error validating setting with value %s: %s" % (setting.value, str(exc))
            messages.append(Error(msg, obj=name, id='settings.E001'))
    return messages


ORCHESTRA_BASE_DOMAIN = Setting('ORCHESTRA_BASE_DOMAIN',
    'orchestra.lan',
    help_text=("Base domain name used for other settings.<br>"
               "If you're editing the settings via the admin interface <b>it is advisable to "
               "commit this change before changing any other variables which could be affected</b>.")
)


ORCHESTRA_SITE_URL = Setting('ORCHESTRA_SITE_URL',
    'https://orchestra.%s' % ORCHESTRA_BASE_DOMAIN,
    help_text=_("Domain name used when it will not be possible to infere the domain from a request."
                "For example in periodic tasks.<br>"
                "Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default.")
)


ORCHESTRA_SITE_NAME = Setting('ORCHESTRA_SITE_NAME',
    'orchestra',
)


ORCHESTRA_SITE_VERBOSE_NAME = Setting('ORCHESTRA_SITE_VERBOSE_NAME',
    "%s Hosting Management" % ORCHESTRA_SITE_NAME.capitalize(),
    help_text="Uses <tt>ORCHESTRA_SITE_NAME</tt> by default."
)


# Service management commands

ORCHESTRA_START_SERVICES = Setting('ORCHESTRA_START_SERVICES',
    default=(
        'postgresql',
        'celeryevcam',
        'celeryd',
        'celerybeat',
        ('uwsgi', 'nginx'),
    ),
)


ORCHESTRA_RESTART_SERVICES = Setting('ORCHESTRA_RESTART_SERVICES',
    default=(
        'celeryd',
        'celerybeat',
        'uwsgi'
    ),
)


ORCHESTRA_STOP_SERVICES = Setting('ORCHESTRA_STOP_SERVICES', 
    default=(
        ('uwsgi', 'nginx'),
        'celerybeat',
        'celeryd',
        'celeryevcam',
        'postgresql'
    ),
)


ORCHESTRA_API_ROOT_VIEW = Setting('ORCHESTRA_API_ROOT_VIEW',
    'orchestra.api.root.APIRoot'
)


ORCHESTRA_DEFAULT_SUPPORT_FROM_EMAIL = Setting('ORCHESTRA_DEFAULT_SUPPORT_FROM_EMAIL',
    'support@{}'.format(ORCHESTRA_BASE_DOMAIN),
    validators=[validate_email],
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default."
)


ORCHESTRA_EDIT_SETTINGS = Setting('ORCHESTRA_EDIT_SETTINGS',
    True
)
