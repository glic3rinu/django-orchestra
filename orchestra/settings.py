from django.conf import settings
from django.utils.translation import ugettext_lazy as _


# Domain name used when it will not be possible to infere the domain from a request
# For example in periodic tasks
SITE_URL = getattr(settings, 'SITE_URL', 'http://localhost')

SITE_NAME = getattr(settings, 'SITE_NAME', 'confine')

SITE_VERBOSE_NAME = getattr(settings, 'SITE_VERBOSE_NAME',
    _("%s Hosting Management" % SITE_NAME.capitalize()))


# Service management commands

START_SERVICES = getattr(settings, 'START_SERVICES',
    ['postgresql', 'celeryevcam', 'celeryd', 'celerybeat', ('uwsgi', 'nginx'),]
)

RESTART_SERVICES = getattr(settings, 'RESTART_SERVICES',
    ['celeryd', 'celerybeat', 'uwsgi']
)

STOP_SERVICES = getattr(settings, 'STOP_SERVICES',
    [('uwsgi', 'nginx'), 'celerybeat', 'celeryd', 'celeryevcam', 'postgresql']
)
