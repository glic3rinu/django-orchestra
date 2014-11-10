from django.conf import settings
from django.utils.translation import ugettext_lazy as _


WEBAPPS_BASE_ROOT = getattr(settings, 'WEBAPPS_BASE_ROOT', '%(home)s/webapps/%(app_name)s/')


WEBAPPS_FPM_LISTEN = getattr(settings, 'WEBAPPS_FPM_LISTEN',
#    '/var/run/%(user)s-%(app_name)s.sock')
    '127.0.0.1:%(fpm_port)s')


WEBAPPS_ALLOW_BLANK_NAME = getattr(settings, 'WEBAPPS_ALLOW_BLANK_NAME', False)

# Default name when blank
WEBAPPS_BLANK_NAME = getattr(settings, 'WEBAPPS_BLANK_NAME', 'webapp')


WEBAPPS_FPM_START_PORT = getattr(settings, 'WEBAPPS_FPM_START_PORT', 10000)


WEBAPPS_PHPFPM_POOL_PATH = getattr(settings, 'WEBAPPS_PHPFPM_POOL_PATH',
    '/etc/php5/fpm/pool.d/%(user)s-%(app_name)s.conf')


WEBAPPS_FCGID_PATH = getattr(settings, 'WEBAPPS_FCGID_PATH',
    '/home/httpd/fcgid/%(user)s/%(app_name)s-wrapper')


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
        'help_text': _("This creates a Webalizer application under "
                       "~/webapps/&lt;app_name&gt;-&lt;site_name&gt;")
    },
})


WEBAPPS_TYPES_OVERRIDE = getattr(settings, 'WEBAPPS_TYPES_OVERRIDE', {})
for webapp_type, value in WEBAPPS_TYPES_OVERRIDE.iteritems():
    if value is None:
        WEBAPPS_TYPES.pop(webapp_type, None)
    else:
        WEBAPPS_TYPES[webapp_type] = value


WEBAPPS_DEFAULT_TYPE = getattr(settings, 'WEBAPPS_DEFAULT_TYPE', 'php5.5')


WEBAPPS_DEFAULT_HTTPS_CERT = getattr(settings, 'WEBAPPS_DEFAULT_HTTPS_CERT',
    ('/etc/apache2/cert', '/etc/apache2/cert.key')
)


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


WEBAPPS_OPTIONS = getattr(settings, 'WEBAPPS_OPTIONS', {
    # { name: ( verbose_name, [help_text], validation_regex ) }
    # PHP
    'enabled_functions': (
        _("PHP - Enabled functions"),
        ' '.join(WEBAPPS_PHP_DISABLED_FUNCTIONS),
        r'^[\w\.,-]+$'
    ),
    'PHP-allow_url_include': (
        _("PHP - Allow URL include"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-allow_url_fopen': (
        _("PHP - allow_url_fopen"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-auto_append_file': (
        _("PHP - Auto append file"),
        r'^[\w\.,-/]+$'
    ),
    'PHP-auto_prepend_file': (
        _("PHP - Auto prepend file"),
        r'^[\w\.,-/]+$'
    ),
    'PHP-date.timezone': (
        _("PHP - date.timezone"),
        _("Timezone string 'Europe/London'."),
        r'^\w+/\w+$'
    ),
    'PHP-default_socket_timeout': (
        _("PHP - Default socket timeout"),
        _("Number between 0 and 999."),
        r'^[0-9]{1,3}$'
    ),
    'PHP-display_errors': (
        _("PHP - Display errors"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-extension': (
        _("PHP - Extension"),
        r'^[^ ]+$'
    ),
    'PHP-magic_quotes_gpc': (
        _("PHP - Magic quotes GPC"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-magic_quotes_runtime': (
        _("PHP - Magic quotes runtime"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-magic_quotes_sybase': (
        _("PHP - Magic quotes sybase"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-max_execution_time': (
        _("PHP - Max execution time"),
        _("Number between 0 and 999."),
        r'^[0-9]{1,3}$'
    ),
    'PHP-max_input_time': (
        _("PHP - Max input time"),
        _("Number between 0 and 999."),
        r'^[0-9]{1,3}$'
    ),
    'PHP-memory_limit': (
        _("PHP - Memory limit"),
        _("Value between 0M and 999M."),
        r'^[0-9]{1,3}M$'
    ),
    'PHP-mysql.connect_timeout': (
        _("PHP - Mysql connect timeout"),
        _("Number between 0 and 999."),
        r'^([0-9]){1,3}$'
    ),
    'PHP-output_buffering': (
        _("PHP - output_buffering"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-register_globals': (
        _("PHP - Register globals"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-post_max_size': (
        _("PHP - Post max size"),
        _("Value between 0M and 999M."),
        r'^[0-9]{1,3}M$'
    ),
    'PHP-sendmail_path': (
        _("PHP - sendmail_path"),
        r'^[^ ]+$'
    ),
    'PHP-session.bug_compat_warn': (
        _("PHP - session.bug_compat_warn"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-session.auto_start': (
        _("PHP - session.auto_start"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-safe_mode': (
        _("PHP - Safe mode"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-suhosin.post.max_vars': (
        _("PHP - Suhosin post max vars"),
        _("Number between 0 and 9999."),
        r'^[0-9]{1,4}$'
    ),
    'PHP-suhosin.request.max_vars': (
        _("PHP - Suhosin request max vars"),
        _("Number between 0 and 9999."),
        r'^[0-9]{1,4}$'
    ),
    'PHP-suhosin.session.encrypt': (
        _("PHP - suhosin.session.encrypt"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-suhosin.simulation': (
        _("PHP - Suhosin simulation"),
        _("On or Off"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-suhosin.executor.include.whitelist': (
        _("PHP - suhosin.executor.include.whitelist"),
        r'.*$'
    ),
    'PHP-upload_max_filesize': (
        _("PHP - upload_max_filesize"),
        _("Value between 0M and 999M."),
        r'^[0-9]{1,3}M$'
    ),
    'PHP-zend_extension': (
        _("PHP - zend_extension"),
        r'^[^ ]+$'
    ),
    # FCGID
    'FcgidIdleTimeout': (
        _("FCGI - Idle timeout"),
        _("Number between 0 and 999."),
        r'^[0-9]{1,3}$'
    ),
    'FcgidBusyTimeout': (
        _("FCGI - Busy timeout"),
        _("Number between 0 and 999."),
        r'^[0-9]{1,3}$'
    ),
    'FcgidConnectTimeout': (
        _("FCGI - Connection timeout"),
        _("Number of seconds between 0 and 999."),
        r'^[0-9]{1,3}$'
    ),
    'FcgidIOTimeout': (
        _("FCGI - IO timeout"),
        _("Number of seconds between 0 and 999."),
        r'^[0-9]{1,3}$'
    ),
    'FcgidProcessLifeTime': (
        _("FCGI - IO timeout"),
        _("Numbe of secondsr between 0 and 9999."),
        r'^[0-9]{1,4}$'
    ),
})
