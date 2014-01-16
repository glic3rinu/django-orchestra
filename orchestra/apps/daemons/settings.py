from django.conf import settings


DAEMONS_OS_CHOICES = getattr(settings, 'DAEMONS_OS_CHOICES', (
    ('LINUX', "Linux"),
))

DAEMONS_DEFAULT_OS_CHOICE = getattr(settings, 'DAEMONS_DEFAULT_OS_CHOICE', 'LINUX')
