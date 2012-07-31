from django.conf import settings

ugettext = lambda s: s

DAEMONS_DEFAULT_SSH_USER = getattr(settings, 'DAEMONS_DEFAULT_SSH_USER', 'root')

DAEMONS_DEFAULT_SSH_PORT = getattr(settings, 'DAEMONS_DEFAULT_SSH_PORT', 22)

DAEMONS_DEFAULT_SSH_HOST_KEYS = getattr(settings, 'DAEMONS_DEFAULT_SSH_HOST_KEYS', '/home/orchestra/.ssh/known_hosts')
