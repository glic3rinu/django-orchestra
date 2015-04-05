from django.conf import settings
from django.utils.translation import ugettext_lazy as _


# Domain name used when it will not be possible to infere the domain from a request
# For example in periodic tasks
ORCHESTRA_SITE_URL = getattr(settings, 'ORCHESTRA_SITE_URL',
    'http://localhost'
)

ORCHESTRA_SITE_NAME = getattr(settings, 'ORCHESTRA_SITE_NAME',
    'orchestra'
)


ORCHESTRA_SITE_VERBOSE_NAME = getattr(settings, 'ORCHESTRA_SITE_VERBOSE_NAME',
    _("%s Hosting Management" % ORCHESTRA_SITE_NAME.capitalize())
)


ORCHESTRA_BASE_DOMAIN = getattr(settings, 'ORCHESTRA_BASE_DOMAIN',
    'orchestra.lan'
)

# Service management commands

ORCHESTRA_START_SERVICES = getattr(settings, 'ORCHESTRA_START_SERVICES', [
    'postgresql',
    'celeryevcam',
    'celeryd',
    'celerybeat',
    ('uwsgi', 'nginx'),
])


ORCHESTRA_RESTART_SERVICES = getattr(settings, 'ORCHESTRA_RESTART_SERVICES', [
    'celeryd',
    'celerybeat',
    'uwsgi'
])

ORCHESTRA_STOP_SERVICES = getattr(settings, 'ORCHESTRA_STOP_SERVICES', [
    ('uwsgi', 'nginx'),
    'celerybeat',
    'celeryd',
    'celeryevcam',
    'postgresql'
])


ORCHESTRA_API_ROOT_VIEW = getattr(settings, 'ORCHESTRA_API_ROOT_VIEW',
    'orchestra.api.root.APIRoot'
)


ORCHESTRA_DEFAULT_SUPPORT_FROM_EMAIL = getattr(settings, 'ORCHESTRA_DEFAULT_SUPPORT_FROM_EMAIL',
    'support@{}'.format(ORCHESTRA_BASE_DOMAIN)
)
