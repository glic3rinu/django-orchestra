from os import path

from django.conf import settings


ORCHESTRATION_OS_CHOICES = getattr(settings, 'ORCHESTRATION_OS_CHOICES', (
    ('LINUX', "Linux"),
))


ORCHESTRATION_DEFAULT_OS = getattr(settings, 'ORCHESTRATION_DEFAULT_OS', 'LINUX')


ORCHESTRATION_SSH_KEY_PATH = getattr(settings, 'ORCHESTRATION_SSH_KEY_PATH', 
    path.join(path.expanduser('~'), '.ssh/id_rsa'))


ORCHESTRATION_ROUTER = getattr(settings, 'ORCHESTRATION_ROUTER',
    'orchestra.contrib.orchestration.models.Route'
)


ORCHESTRATION_TEMP_SCRIPT_PATH = getattr(settings, 'ORCHESTRATION_TEMP_SCRIPT_PATH',
    '/dev/shm'
)
