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
        _("<tt>[permanent] &lt;website path&gt; &lt;destination URL&gt;</tt>"),
        r'^(permanent\s[^ ]+|[^ ]+)\s[^ ]+$',
    ),
    'ssl_ca': (
        "HTTPD - SSL CA",
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
        "HTTPD - SecRuleRemoveById",
        _("Space separated ModSecurity rule IDs."),
        r'^[0-9\s]+$',
    ),
    'sec_engine': (
        "HTTPD - Modsecurity engine",
        _("<tt>On</tt> or <tt>Off</tt>, defaults to On"),
        r'^(On|Off)$',
    ),
    'user_group': (
        "HTTPD - SuexecUserGroup",
        _("<tt>user [group]</tt>, username and optional groupname."),
        # TODO validate existing user/group
        r'^[\w/_]+(\s[\w/_]+)*$',
    ),
    # TODO backend support
    'error_document': (
        "HTTPD - ErrorDocumentRoot",
        _("&lt;error code&gt; &lt;URL/path/message&gt;<br>"
          "<tt>&nbsp;500 http://foo.example.com/cgi-bin/tester</tt><br>"
          "<tt>&nbsp;404 /cgi-bin/bad_urls.pl</tt><br>"
          "<tt>&nbsp;401 /subscription_info.html</tt><br>"
          "<tt>&nbsp;403 \"Sorry can't allow you access today\"</tt>"),
        r'[45]0[0-9]\s.*',
    )
})


WEBSITES_BASE_APACHE_CONF = getattr(settings, 'WEBSITES_BASE_APACHE_CONF',
    '/etc/apache2/')


WEBSITES_WEBALIZER_PATH = getattr(settings, 'WEBSITES_WEBALIZER_PATH',
    '/home/httpd/webalizer/')


WEBSITES_WEBSITE_WWW_LOG_PATH = getattr(settings, 'WEBSITES_WEBSITE_WWW_LOG_PATH',
    '/var/log/apache2/virtual/%(unique_name)s')
