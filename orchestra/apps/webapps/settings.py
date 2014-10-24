from django.conf import settings
from django.utils.translation import ugettext_lazy as _


WEBAPPS_BASE_ROOT = getattr(settings, 'WEBAPPS_BASE_ROOT', '%(home)s/webapps/%(app_name)s/')


WEBAPPS_FPM_LISTEN = getattr(settings, 'WEBAPPS_FPM_LISTEN',
#    '/var/run/%(user)s-%(app_name)s.sock')
    '127.0.0.1:%(fpm_port)s')


WEBAPPS_FPM_START_PORT = getattr(settings, 'WEBAPPS_FPM_START_PORT', 10000)


WEBAPPS_PHPFPM_POOL_PATH = getattr(settings, 'WEBAPPS_PHPFPM_POOL_PATH',
    '/etc/php5/fpm/pool.d/%(user)s-%(app_name)s.conf')


WEBAPPS_FCGID_PATH = getattr(settings, 'WEBAPPS_FCGID_PATH',
    '/home/httpd/fcgid/%(user)s-%(app_name)s-wrapper')


WEBAPPS_TYPES = getattr(settings, 'WEBAPPS_TYPES', {
    'php5.5': {
        'verbose_name': "PHP 5.5",
#        'fpm', ('unix:/var/run/%(user)s-%(app_name)s.sock|fcgi://127.0.0.1%(app_path)s',),
        'directive': ('fpm', 'fcgi://{}%(app_path)s'.format(WEBAPPS_FPM_LISTEN)),
        'help_text': _("This creates a PHP5.5 application under ~/webapps/&lt;app_name&gt;<br>"
                       "PHP-FPM will be used to execute PHP files.")
    },
    'php5.2': {
        'verbose_name': "PHP 5.2",
        'directive': ('fcgi', WEBAPPS_FCGID_PATH),
        'help_text': _("This creates a PHP5.2 application under ~/webapps/&lt;app_name&gt;<br>"
                       "Apache-mod-fcgid will be used to execute PHP files.")
    },
    'php4': {
        'verbose_name': "PHP 4",
        'directive': ('fcgi', WEBAPPS_FCGID_PATH,),
        'help_text': _("This creates a PHP4 application under ~/webapps/&lt;app_name&gt;<br>"
                       "Apache-mod-fcgid will be used to execute PHP files.")
    },
    'static': {
        'verbose_name': _("Static"),
        'directive': ('static',),
        'help_text': _("This creates a Static application under ~/webapps/&lt;app_name&gt;<br>"
                       "Apache2 will be used to serve static content and execute CGI files.")
    },
    'webalizer': {
        'verbose_name': "Webalizer",
        'directive': ('static', '%(app_path)s%(site_name)s'),
        'help_text': _("This creates a Webalizer application under ~/webapps/<app_name>-<site_name>")
    },
})


WEBAPPS_DEFAULT_TYPE = getattr(settings, 'WEBAPPS_DEFAULT_TYPE', 'php5.5')


WEBAPPS_DEFAULT_HTTPS_CERT = getattr(settings, 'WEBAPPS_DEFAULT_HTTPS_CERT',
    ('/etc/apache2/cert', '/etc/apache2/cert.key')
)


WEBAPPS_OPTIONS = getattr(settings, 'WEBAPPS_OPTIONS', {
    # { name: ( verbose_name, validation_regex ) }
    # PHP
    'enabled_functions': (
        _("PHP - Enabled functions"),
        r'^[\w.,-]+$'
    ),
    'PHP-register_globals': (
        _("PHP - Register globals"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-allow_url_include': (
        _("PHP - Allow URL include"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-auto_append_file': (
        _("PHP - Auto append file"),
        r'^none$'
    ),
    'PHP-default_socket_timeout': (
        _("PHP - Default socket timeout"),
        r'P^[0-9][0-9]?[0-9]?$'
    ),
    'PHP-display_errors': (
        _("PHP - Display errors"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-magic_quotes_gpc': (
        _("PHP - Magic quotes GPC"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-max_execution_time': (
        _("PHP - Max execution time"),
        r'^[0-9][0-9]?[0-9]?$'
    ),
    'PHP-max_input_time': (
        _("PHP - Max input time"),
        r'^[0-9][0-9]?[0-9]?$'
    ),
    'PHP-memory_limit': (
        _("PHP - Memory limit"),
        r'^[0-9][0-9]?[0-9]?M$'
    ),
    'PHP-mysql.connect_timeout': (
        _("PHP - Mysql connect timeout"),
        r'^[0-9][0-9]?[0-9]?$'
    ),
    'PHP-post_max_size': (
        _("PHP - Post max size"),
        r'^[0-9][0-9]?M$'
    ),
    'PHP-safe_mode': (
        _("PHP - Safe mode"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-suhosin.post.max_vars': (
        _("PHP - Suhosin post max vars"),
        r'^[0-9][0-9]?[0-9]?[0-9]?$'
    ),
    'PHP-suhosin.request.max_vars': (
        _("PHP - Suhosin request max vars"),
        r'^[0-9][0-9]?[0-9]?[0-9]?$'
    ),
    'PHP-suhosin.simulation': (
        _("PHP - Suhosin simulation"),
        r'^(On|Off|on|off)$'
    ),
    # FCGID
    'FcgidIdleTimeout': (
        _("FCGI - Idle timeout"),
        r'^[0-9][0-9]?[0-9]?$'
    ),
    'FcgidBusyTimeout': (
        _("FCGI - Busy timeout"),
        r'^[0-9][0-9]?[0-9]?$'
    ),
    'FcgidConnectTimeout': (
        _("FCGI - Connection timeout"),
        r'^[0-9][0-9]?[0-9]?$'
    ),
    'FcgidIOTimeout': (
        _("FCGI - IO timeout"),
        r'^[0-9][0-9]?[0-9]?$'
    ),
})


WEBAPPS_PHP_DISABLED_FUNCTIONS = getattr(settings, 'WEBAPPS_PHP_DISABLED_FUNCTION', [
    'exec',
    'passthru',
    'shell_exec',
    'system',
    'proc_open',
    'popen',
    'curl_exec',
    'curl_multi_exec',
    'show_source',
    'pcntl_exec',
    'proc_close',
    'proc_get_status',
    'proc_nice',
    'proc_terminate',
    'ini_alter',
    'virtual',
    'openlog',
    'escapeshellcmd',
    'escapeshellarg',
    'dl'
])
