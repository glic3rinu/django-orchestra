from datetime import timedelta
from os import path

from orchestra.settings import Setting


ORCHESTRATION_OS_CHOICES = Setting('ORCHESTRATION_OS_CHOICES', (
    ('LINUX', "Linux"),
))


ORCHESTRATION_DEFAULT_OS = Setting('ORCHESTRATION_DEFAULT_OS', 'LINUX',
    choices=ORCHESTRATION_OS_CHOICES)


ORCHESTRATION_SSH_KEY_PATH = Setting('ORCHESTRATION_SSH_KEY_PATH', 
    path.join(path.expanduser('~'), '.ssh/id_rsa'))


ORCHESTRATION_ROUTER = Setting('ORCHESTRATION_ROUTER',
    'orchestra.contrib.orchestration.models.Route'
)


ORCHESTRATION_TEMP_SCRIPT_PATH = Setting('ORCHESTRATION_TEMP_SCRIPT_PATH',
    '/dev/shm'
)


ORCHESTRATION_DISABLE_EXECUTION = Setting('ORCHESTRATION_DISABLE_EXECUTION',
    False
)


ORCHESTRATION_BACKEND_CLEANUP_DELTA = Setting('ORCHESTRATION_BACKEND_CLEANUP_DELTA',
    timedelta(days=15)
)
