from django.conf import settings

ugettext = lambda s: s

VIRTUALHOST_IP_CHOICES = getattr(settings, 'VIRTUALHOST_IP_CHOICES', (
    ('127.0.0.1', ugettext('localhost')),))

VIRTUALHOST_IP_DEFAULT = getattr(settings, 'VIRTUALHOST_IP_DEFAULT', '127.0.0.1')

HTTP = 80
HTTPS = 443

VIRTUALHOST_PORT_CHOICES = getattr(settings, 'VIRTUALHOST_PORT_CHOICES', (
    (80, ugettext('HTTP')),
    (443, ugettext('HTTPS')),))

VIRTUALHOST_PORT_DEFAULT = getattr(settings, 'VIRTUALHOST_PORT_DEFAULT', 80)

BASE_CUSTOMLOG_DIR = getattr(settings, 'BASE_CUSTOMLOG_DIR', '/var/log/apache2/virtual/')

DEFAULT_VIRTUAL_HOST_CUSTOM_DIRECTIVES = getattr(settings, 'DEFAULT_VIRTUAL_HOST_CUSTOM_DIRECTIVES', '')

#DEFAULT_DOCUMENT_ROOT = getattr(settings, 'DEFAULT_DOCUMENT_ROOT'
