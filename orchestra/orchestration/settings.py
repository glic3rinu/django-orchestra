from django.conf import settings



ORCHESTRATION_OS_CHOICES = getattr(settings, 'ORCHESTRATION_OS_CHOICES', (
    ('LINUX', "Linux"),
))

ORCHESTRATION_DEFAULT_OS = getattr(settings, 'ORCHESTRATION_DEFAULT_OS', 'LINUX')


ORCHESTRATION_ROUTER = getattr(settings, 'ORCHESTRATION_ROUTER',
    'orchestra.apps.daemons.models.Daemon'
)

