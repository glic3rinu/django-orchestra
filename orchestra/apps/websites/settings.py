from django.conf import settings
from django.utils.translation import ugettext_lazy as _


WEBSITES_PORT_CHOICES = getattr(settings, 'WEBSITES_PORT_CHOICES', (
    (80, 'HTTP'),
    (443, 'HTTPS'),
))


WEBSITES_DEFAULT_PORT = getattr(settings, 'WEBSITES_DEFAULT_PORT', 80)


WEBSITES_DEFAULT_IP = getattr(settings, 'WEBSITES_DEFAULT_IP', '*')


WEBSITES_DOMAIN_MODEL = getattr(settings, 'WEBSITES_DOMAIN_MODEL', 'domains.Domain')


# TODO ssl ca, ssl cert, ssl key
WEBSITES_OPTIONS = getattr(settings, 'WEBSITES_OPTIONS', {
    # { name: ( verbose_name, validation_regex ) }
    'directory_protection': (
        _("HTTPD - Directory protection"),
        r'^([\w/_]+)\s+(\".*\")\s+([\w/_\.]+)$'
    ),
    'redirect': (
        _("HTTPD - Redirection"),
        r'^(permanent\s[^ ]+|[^ ]+)\s[^ ]+$'
    ),
    'ssl_ca': (
        _("HTTPD - SSL CA"),
        r'^[^ ]+$'
    ),
    'ssl_cert': (
        _("HTTPD - SSL cert"),
        r'^[^ ]+$'
    ),
    'ssl_key': (
        _("HTTPD - SSL key"),
        r'^[^ ]+$'
    ),
    'sec_rule_remove': (
        _("HTTPD - SecRuleRemoveById"),
        r'^[0-9\s]+$'
    ),
    'sec_engine': (
        _("HTTPD - Disable Modsecurity"),
        r'^[\w/_]+$'
    ),
})


WEBSITES_BASE_APACHE_CONF = getattr(settings, 'WEBSITES_BASE_APACHE_CONF',
    '/etc/apache2/')


WEBSITES_WEBALIZER_PATH = getattr(settings, 'WEBSITES_WEBALIZER_PATH',
    '/home/httpd/webalizer/')


WEBSITES_WEBSITE_WWW_LOG_PATH = getattr(settings, 'WEBSITES_WEBSITE_WWW_LOG_PATH',
    '/var/log/apache2/virtual/%(unique_name)s')
