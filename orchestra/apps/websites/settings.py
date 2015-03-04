from django.conf import settings
from django.utils.translation import ugettext_lazy as _


WEBSITES_UNIQUE_NAME_FORMAT = getattr(settings, 'WEBSITES_UNIQUE_NAME_FORMAT',
    '%(account)s-%(name)s')


# TODO 'http', 'https', 'https-only', 'http and https' and rename to PROTOCOL
WEBSITES_PORT_CHOICES = getattr(settings, 'WEBSITES_PORT_CHOICES', (
    (80, 'HTTP'),
    (443, 'HTTPS'),
))


WEBSITES_PROTOCOL_CHOICES = getattr(settings, 'WEBSITES_PROTOCOL_CHOICES', (
    ('http', 'HTTP'),
    ('https', 'HTTPS'),
    ('http-https', 'HTTP and HTTPS),
    ('https-only', 'HTTPS only'),
))

WEBSITES_DEFAULT_PORT = getattr(settings, 'WEBSITES_DEFAULT_PORT', 80)


WEBSITES_DEFAULT_IP = getattr(settings, 'WEBSITES_DEFAULT_IP', '*')


WEBSITES_DOMAIN_MODEL = getattr(settings, 'WEBSITES_DOMAIN_MODEL', 'domains.Domain')


WEBSITES_ENABLED_OPTIONS = getattr(settings, 'WEBSITES_ENABLED_OPTIONS', (
    'orchestra.apps.websites.options.directory_protection',
    'orchestra.apps.websites.options.redirect',
    'orchestra.apps.websites.options.proxy',
    'orchestra.apps.websites.options.ssl_ca',
    'orchestra.apps.websites.options.ssl_cert',
    'orchestra.apps.websites.options.ssl_key',
    'orchestra.apps.websites.options.sec_rule_remove',
    'orchestra.apps.websites.options.sec_engine',
    'orchestra.apps.websites.options.user_group',
    'orchestra.apps.websites.options.error_document',
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
