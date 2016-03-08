from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.settings import Setting


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
#        'celeryevcam',
#        'celeryd',
#        'celerybeat',
        ('uwsgi', 'nginx'),
    ),
)


ORCHESTRA_RESTART_SERVICES = Setting('ORCHESTRA_RESTART_SERVICES',
    default=(
#        'celeryd',
#        'celerybeat',
        'uwsgi'
    ),
)


ORCHESTRA_STOP_SERVICES = Setting('ORCHESTRA_STOP_SERVICES', 
    default=(
        ('uwsgi', 'nginx'),
#        'celerybeat',
#        'celeryd',
#        'celeryevcam',
        'postgresql'
    ),
)


ORCHESTRA_API_ROOT_VIEW = Setting('ORCHESTRA_API_ROOT_VIEW',
    'orchestra.api.root.APIRoot'
)


ORCHESTRA_SSH_DEFAULT_USER = Setting('ORCHESTRA_SSH_DEFAULT_USER',
    'root'
)


ORCHESTRA_DEFAULT_SUPPORT_FROM_EMAIL = Setting('ORCHESTRA_DEFAULT_SUPPORT_FROM_EMAIL',
    'support@{}'.format(ORCHESTRA_BASE_DOMAIN),
    validators=[validate_email],
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default."
)


ORCHESTRA_EDIT_SETTINGS = Setting('ORCHESTRA_EDIT_SETTINGS',
    True
)


ORCHESTRA_SSH_CONTROL_PATH = Setting('ORCHESTRA_SSH_CONTROL_PATH',
    '~/.ssh/orchestra-%r-%h-%p',
    help_text='Location for the control socket used by the multiplexed sessions, used for SSH connection reuse.'
)
