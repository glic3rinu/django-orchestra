from django.conf import settings

ugettext = lambda s: s

WEB_VIRTUALHOST_IP_CHOICES = getattr(settings, 'WEB_VIRTUALHOST_IP_CHOICES', (
    ('127.0.0.1', ugettext('localhost')),))

WEB_VIRTUALHOST_IP_DEFAULT = getattr(settings, 'WEB_VIRTUALHOST_IP_DEFAULT', '127.0.0.1')

#HTTP = 80
#HTTPS = 443

WEB_VIRTUALHOST_PORT_CHOICES = getattr(settings, 'WEB_VIRTUALHOST_PORT_CHOICES', (
    (80, ugettext('HTTP')),
    (443, ugettext('HTTPS')),))

WEB_VIRTUALHOST_PORT_DEFAULT = getattr(settings, 'WEB_VIRTUALHOST_PORT_DEFAULT', 80)

WEB_BASE_CUSTOMLOG_DIR = getattr(settings, 'WEB_BASE_CUSTOMLOG_DIR', '/var/log/apache2/virtual/')

WEB_DEFAULT_VIRTUAL_HOST_CUSTOM_DIRECTIVES = getattr(settings, 'WEB_DEFAULT_VIRTUAL_HOST_CUSTOM_DIRECTIVES', '')

#DEFAULT_DOCUMENT_ROOT = getattr(settings, 'DEFAULT_DOCUMENT_ROOT'
