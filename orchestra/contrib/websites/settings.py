from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.settings import Setting
from orchestra.core.validators import validate_ip_address

from .. import websites


_names = ('id', 'pk', 'home', 'user', 'group', 'site_name', 'protocol')
_log_names = _names + ('unique_name',)


WEBSITES_UNIQUE_NAME_FORMAT = Setting('WEBSITES_UNIQUE_NAME_FORMAT',
    default='%(user)s-%(site_name)s',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_names),
    validators=[Setting.string_format_validator(_names)],
)


WEBSITES_PROTOCOL_CHOICES = Setting('WEBSITES_PROTOCOL_CHOICES',
    default=(
        ('http', "HTTP"),
        ('https', "HTTPS"),
        ('http/https', _("HTTP and HTTPS")),
        ('https-only', _("HTTPS only")),
    ),
    validators=[Setting.validate_choices]
)


WEBSITES_DEFAULT_PROTOCOL = Setting('WEBSITES_DEFAULT_PROTOCOL',
    default='http',
    choices=WEBSITES_PROTOCOL_CHOICES
)


WEBSITES_DEFAULT_IPS = Setting('WEBSITES_DEFAULT_IPS',
    default=('*',)
)


WEBSITES_DOMAIN_MODEL = Setting('WEBSITES_DOMAIN_MODEL',
    'domains.Domain',
    validators=[Setting.validate_model_label]
)


WEBSITES_ENABLED_DIRECTIVES = Setting('WEBSITES_ENABLED_DIRECTIVES',
    (
        'orchestra.contrib.websites.directives.Redirect',
        'orchestra.contrib.websites.directives.Proxy',
        'orchestra.contrib.websites.directives.ErrorDocument',
        'orchestra.contrib.websites.directives.SSLCA',
        'orchestra.contrib.websites.directives.SSLCert',
        'orchestra.contrib.websites.directives.SSLKey',
        'orchestra.contrib.websites.directives.SecRuleRemove',
        'orchestra.contrib.websites.directives.SecEngine',
        'orchestra.contrib.websites.directives.WordPressSaaS',
        'orchestra.contrib.websites.directives.DokuWikiSaaS',
        'orchestra.contrib.websites.directives.DrupalSaaS',
        'orchestra.contrib.websites.directives.MoodleSaaS',
    ),
    # lazy loading
    choices=lambda : ((d.get_class_path(), d.get_class_path()) for d in websites.directives.SiteDirective.get_plugins(all=True)),
    multiple=True,
)


WEBSITES_BASE_APACHE_CONF = Setting('WEBSITES_BASE_APACHE_CONF',
    '/etc/apache2/'
)


WEBSITES_WEBALIZER_PATH = Setting('WEBSITES_WEBALIZER_PATH',
    '/home/httpd/webalizer/'
)


WEBSITES_WEBSITE_WWW_ACCESS_LOG_PATH = Setting('WEBSITES_WEBSITE_WWW_ACCESS_LOG_PATH',
    '/var/log/apache2/virtual/%(unique_name)s.log',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_log_names),
    validators=[Setting.string_format_validator(_log_names)],
)


WEBSITES_WEBSITE_WWW_ERROR_LOG_PATH = Setting('WEBSITES_WEBSITE_WWW_ERROR_LOG_PATH',
    '',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_log_names),
    validators=[Setting.string_format_validator(_log_names)],
)


WEBSITES_TRAFFIC_IGNORE_HOSTS = Setting('WEBSITES_TRAFFIC_IGNORE_HOSTS',
    ('127.0.0.1',),
    help_text=_("IP addresses to ignore during traffic accountability."),
    validators=[lambda hosts: (validate_ip_address(host) for host in hosts)],
)


# TODO sane defaults
WEBSITES_SAAS_DIRECTIVES = Setting('WEBSITES_SAAS_DIRECTIVES',
    {
        'wordpress-saas': ('fpm', '/var/run/fpm/pangea-5.4-fpm.sock', '/home/httpd/wordpress-mu/'),
        'drupal-saas': ('fpm', '/var/run/fpm/pangea-5.4-fpm.sock', '/home/httpd/drupal-mu/'),
        'dokuwiki-saas': ('fpm', '/var/run/fpm/pangea-5.4-fpm.sock', '/home/httpd/dokuwiki-mu/'),
        'moodle-saas': ('fpm', '/var/run/fpm/pangea-5.4-fpm.sock', '/home/httpd/moodle-mu/'),
    },
)


WEBSITES_DEFAULT_SSL_CERT = Setting('WEBSITES_DEFAULT_SSL_CERT',
    ''
)

WEBSITES_DEFAULT_SSL_KEY = Setting('WEBSITES_DEFAULT_SSL_KEY',
    ''
)

WEBSITES_DEFAULT_SSL_CA = Setting('WEBSITES_DEFAULT_SSL_CA',
    ''
)

WEBSITES_VHOST_EXTRA_DIRECTIVES = Setting('WEBSITES_VHOST_EXTRA_DIRECTIVES',
    (),
    help_text=(
        "(<location>, <directive>), <br>"
        "i.e. ('/cgi-bin/', 'ScriptAlias /cgi-bin/ %(home)s/cgi-bin/')"
    )
)
