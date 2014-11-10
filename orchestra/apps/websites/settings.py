from django.conf import settings
from django.utils.translation import ugettext_lazy as _


WEBSITES_PORT_CHOICES = getattr(settings, 'WEBSITES_PORT_CHOICES', (
    (80, 'HTTP'),
    (443, 'HTTPS'),
))


WEBSITES_DEFAULT_PORT = getattr(settings, 'WEBSITES_DEFAULT_PORT', 80)


WEBSITES_DEFAULT_IP = getattr(settings, 'WEBSITES_DEFAULT_IP', '*')


WEBSITES_DOMAIN_MODEL = getattr(settings, 'WEBSITES_DOMAIN_MODEL', 'domains.Domain')


WEBSITES_OPTIONS = getattr(settings, 'WEBSITES_OPTIONS', {
    # { name: ( verbose_name, [help_text], validation_regex ) }
    'directory_protection': (
        _("HTTPD - Directory protection"),
        _("Space separated ..."),
        r'^([\w/_]+)\s+(\".*\")\s+([\w/_\.]+)$',
    ),
    'redirect': (
        _("HTTPD - Redirection"),
        _("[permanent] &lt;website path&gt; &lt;destination URL&gt;"),
        r'^(permanent\s[^ ]+|[^ ]+)\s[^ ]+$',
    ),
    'ssl_ca': (
        _("HTTPD - SSL CA"),
        _("Filesystem path of the CA certificate file."),
        r'^[^ ]+$'
    ),
    'ssl_cert': (
        _("HTTPD - SSL cert"),
        _("Filesystem path of the certificate file."),
        r'^[^ ]+$'
    ),
    'ssl_key': (
        _("HTTPD - SSL key"),
        _("Filesystem path of the key file."),
        r'^[^ ]+$',
    ),
    'sec_rule_remove': (
        _("HTTPD - SecRuleRemoveById"),
        _("Space separated ModSecurity rule IDs."),
        r'^[0-9\s]+$',
    ),
    'sec_engine': (
        _("HTTPD - Modsecurity engine"),
        _("On or Off, defaults to On"),
        r'^(On|Off)$',
    ),
    'user_group': (
        _("HTTPD - SuexecUserGroup"),
        _("Username and optional groupname (user [group])"),
        # TODO validate existing user/group
        r'^[\w/_]+(\s[\w/_]+)*$',
    ),
})


WEBSITES_BASE_APACHE_CONF = getattr(settings, 'WEBSITES_BASE_APACHE_CONF',
    '/etc/apache2/')


WEBSITES_WEBALIZER_PATH = getattr(settings, 'WEBSITES_WEBALIZER_PATH',
    '/home/httpd/webalizer/')


WEBSITES_WEBSITE_WWW_LOG_PATH = getattr(settings, 'WEBSITES_WEBSITE_WWW_LOG_PATH',
    '/var/log/apache2/virtual/%(unique_name)s')
