from collections import OrderedDict

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .core import validators


class Setting(object):
    """
    Keeps track of the defined settings.
    Instances of this class are the native value of the setting.
    """
    conf_settings = settings
    settings = OrderedDict()
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        value = str(self.value)
        value = ("'%s'" if isinstance(value, str) else '%s') % value
        return '<%s: %s>' % (self.name, value)
    
    def __new__(cls, name, default, help_text="", choices=None, editable=True, multiple=False,
                validators=[], types=[], call_init=False):
        if call_init:
            return super(Setting, cls).__new__(cls)
        cls.settings[name] = cls(name, default, help_text=help_text, choices=choices,
            editable=editable, multiple=multiple, validators=validators, types=types, call_init=True)
        return cls.get_value(name, default)
    
    def __init__(self, *args, **kwargs):
        self.name, self.default = args
        for name, value in kwargs.items():
            setattr(self, name, value)
        self.value = self.get_value(self.name, self.default)
        self.validate_value(self.value)
        self.settings[name] = self
   
    def validate_value(self, value):
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


ORCHESTRA_BASE_DOMAIN = Setting('ORCHESTRA_BASE_DOMAIN',
    'orchestra.lan'
)


ORCHESTRA_SITE_URL = Setting('ORCHESTRA_SITE_URL', 'https://orchestra.%s' % ORCHESTRA_BASE_DOMAIN,
    help_text=_("Domain name used when it will not be possible to infere the domain from a request."
                "For example in periodic tasks.")
)


ORCHESTRA_SITE_NAME = Setting('ORCHESTRA_SITE_NAME', 'orchestra')


ORCHESTRA_SITE_VERBOSE_NAME = Setting('ORCHESTRA_SITE_VERBOSE_NAME',
    _("%s Hosting Management" % ORCHESTRA_SITE_NAME.capitalize())
)


# Service management commands

ORCHESTRA_START_SERVICES = Setting('ORCHESTRA_START_SERVICES', (
    'postgresql',
    'celeryevcam',
    'celeryd',
    'celerybeat',
    ('uwsgi', 'nginx'),
))


ORCHESTRA_RESTART_SERVICES = Setting('ORCHESTRA_RESTART_SERVICES', (
    'celeryd',
    'celerybeat',
    'uwsgi'
))

ORCHESTRA_STOP_SERVICES = Setting('ORCHESTRA_STOP_SERVICES', (
    ('uwsgi', 'nginx'),
    'celerybeat',
    'celeryd',
    'celeryevcam',
    'postgresql'
))


ORCHESTRA_API_ROOT_VIEW = Setting('ORCHESTRA_API_ROOT_VIEW',
    'orchestra.api.root.APIRoot'
)


ORCHESTRA_DEFAULT_SUPPORT_FROM_EMAIL = Setting('ORCHESTRA_DEFAULT_SUPPORT_FROM_EMAIL',
    'support@{}'.format(ORCHESTRA_BASE_DOMAIN)
)


ORCHESTRA_EDIT_SETTINGS = Setting('ORCHESTRA_EDIT_SETTINGS', True)
