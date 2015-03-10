from django.conf import settings
from django.utils.translation import ugettext_lazy as _


WEBSITES_UNIQUE_NAME_FORMAT = getattr(settings, 'WEBSITES_UNIQUE_NAME_FORMAT',
    '%(account)s-%(name)s')


# TODO 'http', 'https', 'https-only', 'http and https' and rename to PROTOCOL
#WEBSITES_PORT_CHOICES = getattr(settings, 'WEBSITES_PORT_CHOICES', (
#    (80, 'HTTP'),
#    (443, 'HTTPS'),
#))


WEBSITES_PROTOCOL_CHOICES = getattr(settings, 'WEBSITES_PROTOCOL_CHOICES', (
    ('http', "HTTP"),
    ('https', "HTTPS"),
    ('http/https', _("HTTP and HTTPS")),
    ('https-only', _("HTTPS only")),
))

WEBSITES_DEFAULT_PROTOCOL = getattr(settings, 'WEBSITES_DEFAULT_PROTOCOL', 'http')

WEBSITES_DEFAULT_PORT = getattr(settings, 'WEBSITES_DEFAULT_PORT', 80)


WEBSITES_DEFAULT_IP = getattr(settings, 'WEBSITES_DEFAULT_IP', '*')


WEBSITES_DOMAIN_MODEL = getattr(settings, 'WEBSITES_DOMAIN_MODEL', 'domains.Domain')


WEBSITES_ENABLED_DIRECTIVES = getattr(settings, 'WEBSITES_ENABLED_DIRECTIVES', (
    'orchestra.apps.websites.directives.Redirect',
    'orchestra.apps.websites.directives.Proxy',
    'orchestra.apps.websites.directives.UserGroup',
    'orchestra.apps.websites.directives.ErrorDocument',
    'orchestra.apps.websites.directives.SSLCA',
    'orchestra.apps.websites.directives.SSLCert',
    'orchestra.apps.websites.directives.SSLKey',
    'orchestra.apps.websites.directives.SecRuleRemove',
    'orchestra.apps.websites.directives.SecEngine',
))


WEBSITES_BASE_APACHE_CONF = getattr(settings, 'WEBSITES_BASE_APACHE_CONF',
    '/etc/apache2/')


WEBSITES_WEBALIZER_PATH = getattr(settings, 'WEBSITES_WEBALIZER_PATH',
    '/home/httpd/webalizer/')


WEBSITES_WEBSITE_WWW_ACCESS_LOG_PATH = getattr(settings, 'WEBSITES_WEBSITE_WWW_ACCESS_LOG_PATH',
    '/var/log/apache2/virtual/%(unique_name)s.log')


WEBSITES_WEBSITE_WWW_ERROR_LOG_PATH = getattr(settings, 'WEBSITES_WEBSITE_WWW_ERROR_LOG_PATH',
    '')


WEBSITES_TRAFFIC_IGNORE_HOSTS = getattr(settings, 'WEBSITES_TRAFFIC_IGNORE_HOSTS',
    ('127.0.0.1',))


#WEBSITES_DEFAULT_SSl_CA = getattr(settings, 'WEBSITES_DEFAULT_SSl_CA',
#    '')

#WEBSITES_DEFAULT_SSl_CERT = getattr(settings, 'WEBSITES_DEFAULT_SSl_CERT',
#    '')

#WEBSITES_DEFAULT_SSl_KEY = getattr(settings, 'WEBSITES_DEFAULT_SSl_KEY',
#    '')
