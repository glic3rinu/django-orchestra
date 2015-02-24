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
        'verbose_name': "PHP 5.5 fpm",
#        'fpm', ('unix:/var/run/%(user)s-%(app_name)s.sock|fcgi://127.0.0.1%(app_path)s',),
        'directive': ('fpm', 'fcgi://{}%(app_path)s'.format(WEBAPPS_FPM_LISTEN)),
        'help_text': _("This creates a PHP5.5 application under ~/webapps/&lt;app_name&gt;<br>"
                       "PHP-FPM will be used to execute PHP files.")
    },
    'php5.2': {
        'verbose_name': "PHP 5.2 fcgi",
        'directive': ('fcgi', WEBAPPS_FCGID_PATH),
        'help_text': _("This creates a PHP5.2 application under ~/webapps/&lt;app_name&gt;<br>"
                       "Apache-mod-fcgid will be used to execute PHP files.")
    },
    'php4': {
        'verbose_name': "PHP 4 fcgi",
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
    'wordpress-mu': {
        'verbose_name': _("Wordpress (SaaS)"),
        'directive': ('fpm', 'fcgi://127.0.0.1:8990/home/httpd/wordpress-mu/'),
        'help_text': _("This creates a Wordpress site on a multi-tenant Wordpress server.<br>"
                       "By default this blog is accessible via &lt;app_name&gt;.blogs.orchestra.lan")
    },
    'dokuwiki-mu': {
        'verbose_name': _("DokuWiki (SaaS)"),
        'directive': ('alias', '/home/httpd/wikifarm/farm/'),
        'help_text': _("This create a Dokuwiki wiki into a shared Dokuwiki server.<br>"
                       "By default this wiki is accessible via &lt;app_name&gt;.wikis.orchestra.lan")
    },
    'drupal-mu': {
        'verbose_name': _("Drupdal (SaaS)"),
        'directive': ('fpm', 'fcgi://127.0.0.1:8991/home/httpd/drupal-mu/'),
        'help_text': _("This creates a Drupal site into a multi-tenant Drupal server.<br>"
                       "The installation will be completed after visiting "
                       "http://&lt;app_name&gt;.drupal.orchestra.lan/install.php?profile=standard<br>"
                       "By default this site will be accessible via &lt;app_name&gt;.drupal.orchestra.lan")
    }
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
    # Filesystem
    'public-root': (
        _("Public root"),
        _("Document root relative to webapps/&lt;webapp&gt;/"),
        r'[^ ]+',
    ),
    # Processes
    'timeout': (
        _("Process timeout"),
        _("Maximum time in seconds allowed for a request to complete "
          "(a number between 0 and 999)."),
        # FCGID FcgidIOTimeout
        # FPM pm.request_terminate_timeout
        # PHP max_execution_time ini
        r'^[0-9]{1,3}$',
    ),
    'processes': (
        _("Number of processes"),
        _("Maximum number of children that can be alive at the same time "
          "(a number between 0 and 9)."),
        # FCGID MaxProcesses
        # FPM pm.max_children
        r'^[0-9]$',
    ),
    # PHP
    'php-enabled_functions': (
        _("PHP - Enabled functions"),
        ' '.join(WEBAPPS_PHP_DISABLED_FUNCTIONS),
        r'^[\w\.,-]+$'
    ),
    'PHP-allow_url_include': (
        _("PHP - Allow URL include"),
        _("Allows the use of URL-aware fopen wrappers with include, include_once, require, "
          "require_once (On or Off)."),
        r'^(On|Off|on|off)$'
    ),
    'PHP-allow_url_fopen': (
        _("PHP - allow_url_fopen"),
        _("Enables the URL-aware fopen wrappers that enable accessing URL object like files "
          "(On or Off)."),
        r'^(On|Off|on|off)$'
    ),
    'PHP-auto_append_file': (
        _("PHP - Auto append file"),
        _("Specifies the name of a file that is automatically parsed after the main file."),
        r'^[\w\.,-/]+$'
    ),
    'PHP-auto_prepend_file': (
        _("PHP - Auto prepend file"),
        _("Specifies the name of a file that is automatically parsed before the main file."),
        r'^[\w\.,-/]+$'
    ),
    'PHP-date.timezone': (
        _("PHP - date.timezone"),
        _("Sets the default timezone used by all date/time functions "
          "(Timezone string 'Europe/London')."),
        r'^\w+/\w+$'
    ),
    'PHP-default_socket_timeout': (
        _("PHP - Default socket timeout"),
        _("Number between 0 and 999."),
        r'^[0-9]{1,3}$'
    ),
    'PHP-display_errors': (
        _("PHP - Display errors"),
        _("determines whether errors should be printed to the screen as part of the output or "
          "if they should be hidden from the user (On or Off)."),
        r'^(On|Off|on|off)$'
    ),
    'PHP-extension': (
        _("PHP - Extension"),
        r'^[^ ]+$'
    ),
    'PHP-magic_quotes_gpc': (
        _("PHP - Magic quotes GPC"),
        _("Sets the magic_quotes state for GPC (Get/Post/Cookie) operations (On or Off) "
          "<b>DEPRECATED as of PHP 5.3.0</b>."),
        r'^(On|Off|on|off)$'
    ),
    'PHP-magic_quotes_runtime': (
        _("PHP - Magic quotes runtime"),
        _("Functions that return data from any sort of external source will have quotes escaped "
          "with a backslash (On or Off) <b>DEPRECATED as of PHP 5.3.0</b>."),
        r'^(On|Off|on|off)$'
    ),
    'PHP-magic_quotes_sybase': (
        _("PHP - Magic quotes sybase"),
        _("Single-quote is escaped with a single-quote instead of a backslash (On or Off)."),
        r'^(On|Off|on|off)$'
    ),
    'PHP-max_execution_time': (
        _("PHP - Max execution time"),
        _("Maximum time in seconds a script is allowed to run before it is terminated by "
          "the parser (Integer between 0 and 999)."),
        r'^[0-9]{1,3}$'
    ),
    'PHP-max_input_time': (
        _("PHP - Max input time"),
        _("Maximum time in seconds a script is allowed to parse input data, like POST and GET "
          "(Integer between 0 and 999)."),
        r'^[0-9]{1,3}$'
    ),
    'PHP-max_input_vars': (
        _("PHP - Max input vars"),
        _("How many input variables may be accepted (limit is applied to $_GET, $_POST and $_COOKIE superglobal separately) "
          "(Integer between 0 and 9999)."),
        r'^[0-9]{1,4}$'
    ),
    'PHP-memory_limit': (
        _("PHP - Memory limit"),
        _("This sets the maximum amount of memory in bytes that a script is allowed to allocate "
          "(Value between 0M and 999M)."),
        r'^[0-9]{1,3}M$'
    ),
    'PHP-mysql.connect_timeout': (
        _("PHP - Mysql connect timeout"),
        _("Number between 0 and 999."),
        r'^([0-9]){1,3}$'
    ),
    'PHP-output_buffering': (
        _("PHP - output_buffering"),
        _("Turn on output buffering (On or Off)."),
        r'^(On|Off|on|off)$'
    ),
    'PHP-register_globals': (
        _("PHP - Register globals"),
        _("Whether or not to register the EGPCS (Environment, GET, POST, Cookie, Server) "
          "variables as global variables (On or Off)."),
        r'^(On|Off|on|off)$'
    ),
    'PHP-post_max_size': (
        _("PHP - Post max size"),
        _("Sets max size of post data allowed (Value between 0M and 999M)."),
        r'^[0-9]{1,3}M$'
    ),
    'PHP-sendmail_path': (
        _("PHP - sendmail_path"),
        _("Where the sendmail program can be found."),
        r'^[^ ]+$'
    ),
    'PHP-session.bug_compat_warn': (
        _("PHP - session.bug_compat_warn"),
        _("Enables an PHP bug on session initialization for legacy behaviour (On or Off)."),
        r'^(On|Off|on|off)$'
    ),
    'PHP-session.auto_start': (
        _("PHP - session.auto_start"),
        _("Specifies whether the session module starts a session automatically on request "
          "startup (On or Off)."),
        r'^(On|Off|on|off)$'
    ),
    'PHP-safe_mode': (
        _("PHP - Safe mode"),
        _("Whether to enable PHP's safe mode (On or Off) <b>DEPRECATED as of PHP 5.3.0</b>"),
        r'^(On|Off|on|off)$'
    ),
    'PHP-suhosin.post.max_vars': (
        _("PHP - Suhosin POST max vars"),
        _("Number between 0 and 9999."),
        r'^[0-9]{1,4}$'
    ),
    'PHP-suhosin.get.max_vars': (
        _("PHP - Suhosin GET max vars"),
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
})



WEBAPPS_WORDPRESSMU_ADMIN_PASSWORD = getattr(settings, 'WEBAPPS_WORDPRESSMU_ADMIN_PASSWORD',
    'secret')

WEBAPPS_WORDPRESSMU_BASE_URL = getattr(settings, 'WEBAPPS_WORDPRESSMU_BASE_URL', 
    'http://blogs.orchestra.lan/')


WEBAPPS_DOKUWIKIMU_TEMPLATE_PATH = getattr(settings, 'WEBAPPS_DOKUWIKIMU_TEMPLATE_PATH',
    '/home/httpd/htdocs/wikifarm/template.tar.gz')

WEBAPPS_DOKUWIKIMU_FARM_PATH = getattr(settings, 'WEBAPPS_DOKUWIKIMU_FARM_PATH',
    '/home/httpd/htdocs/wikifarm/farm')


WEBAPPS_DRUPAL_SITES_PATH = getattr(settings, 'WEBAPPS_DRUPAL_SITES_PATH',
    '/home/httpd/htdocs/drupal-mu/sites/%(site_name)s')
