from django.conf import settings
from django.utils.translation import ugettext_lazy as _


WEBSITES_PORT_CHOICES = getattr(settings, 'WEBSITES_PORT_CHOICES', (
    (80, 'HTTP'),
    (443, 'HTTPS'),
))


WEBSITES_DEFAULT_PORT = getattr(settings, 'WEBSITES_DEFAULT_PORT', 80)


WEBSITES_DOMAIN_MODEL = getattr(settings, 'WEBSITES_DOMAIN_MODEL', 'domains.Domain')


WEBSITES_OPTIONS = getattr(settings, 'WEBSITES_OPTIONS', {
    # { name: ( verbose_name, validation_regex ) }
    'directory_protection': (
        _("HTTPD - Directory protection"),
        r'^([\w/_]+)\s+(\".*\")\s+([\w/_\.]+)$'
    ),
    'redirection': (
        _("HTTPD - Redirection"),
        r'^.*\s+.*$'
    ),
    'ssl': (
        _("HTTPD - SSL"),
        r'^.*\s+.*$'
    ),
    'sec_rule_remove': (
        _("HTTPD - SecRuleRemoveById"),
        r'^[0-9,\s]+$'
    ),
    'sec_rule_off': (
        _("HTTPD - Disable Modsecurity"),
        r'^[\w/_]+$'
    ),
})


WEBSITES_BASE_APACHE_CONF = getattr(settings, 'WEBSITES_BASE_APACHE_CONF',
    '/etc/apache2/')

WEBSITES_WEBALIZER_PATH = getattr(settings, 'WEBSITES_WEBALIZER_PATH',
    '/home/httpd/webalizer/')


WEBSITES_BASE_APACHE_LOGS = getattr(settings, 'WEBSITES_BASE_APACHE_LOGS',
    '/var/log/apache2/virtual/')
