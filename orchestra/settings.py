from django.conf import settings


START_SERVICES = getattr(settings, 'START_SERVICES',
    ['postgresql', 'celeryevcam', 'celeryd', 'celerybeat', ('uwsgi', 'nginx'),]
)

RESTART_SERVICES = getattr(settings, 'RESTART_SERVICES',
    ['celeryd', 'celerybeat', 'uwsgi']
)

STOP_SERVICES = getattr(settings, 'STOP_SERVICES',
    [('uwsgi', 'nginx'), 'celerybeat', 'celeryd', 'celeryevcam', 'postgresql']
)
