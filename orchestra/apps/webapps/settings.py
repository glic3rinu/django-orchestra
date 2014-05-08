from django.conf import settings
from django.utils.translation import ugettext_lazy as _


WEBAPPS_BASE_ROOT = getattr(settings, 'WEBAPPS_BASE_ROOT', '/home/%(user)s/webapps/%(app_name)s/')


WEBAPPS_FPM_LISTEN = getattr(settings, 'WEBAPPS_FPM_LISTEN',
#    '/var/run/%(user)s-%(app_name)s.sock')
    '127.0.0.1:%(fpm_port)s')

WEBAPPS_FPM_START_PORT = getattr(settings, 'WEBAPPS_FPM_START_PORT', 10000)

WEBAPPS_FCGID_PATH = getattr(settings, 'WEBAPPS_FCGID_PATH',
    '/home/httpd/fcgid/%(user)s/%(type)s-wrapper')


WEBAPPS_TYPES = getattr(settings, 'WEBAPPS_TYPES', {
    # { name: ( verbose_name, method_name, method_args, description) }
    'php5.5': (
        _("PHP 5.5"),
#        'fpm', ('unix:/var/run/%(user)s-%(app_name)s.sock|fcgi://127.0.0.1%(app_path)s',),
        'fpm', ('fcgi://127.0.0.1:%(fpm_port)s%(app_path)s',),
        _("This creates a PHP5.5 application under ~/webapps/<app_name>\n"
          "PHP-FPM will be used to execute PHP files.")
    ),
    'php5': (
        _("PHP 5"),
        'fcgid', (WEBAPPS_FCGID_PATH,),
        _("This creates a PHP5.2 application under ~/webapps/<app_name>\n"
          "Apache-mod-fcgid will be used to execute PHP files.")
    ),
    'php4': (
        _("PHP 4"),
        'fcgid', (WEBAPPS_FCGID_PATH,),
        _("This creates a PHP4 application under ~/webapps/<app_name>\n"
          "Apache-mod-fcgid will be used to execute PHP files.")
    ),
    'static': (
        _("Static"),
        'alias', (),
        _("This creates a Static application under ~/webapps/<app_name>\n"
          "Apache2 will be used to serve static content and execute CGI files.")
    ),
    'wordpressmu': (
        _("Wordpress (shared)"),
        'fpm', ('fcgi://127.0.0.1:8990/home/httpd/wordpress-mu/',),
        _("This creates a Wordpress site into a shared Wordpress server\n"
          "By default this blog will be accessible via http://<app_name>.blogs.example.com")
        
    ),
    'dokuwikimu': (
        _("DokuWiki (shared)"),
        'alias', ('/home/httpd/wikifarm/farm/',),
        _("This create a Dokuwiki wiki into a shared Dokuwiki server\n")
    ),
    'drupalmu': (
        _("Drupdal (shared)"),
        'fpm', ('fcgi://127.0.0.1:8991/home/httpd/drupal-mu/',),
        _("This creates a Drupal site into a shared Drupal server\n"
          "The installation will be completed after visiting "
          "http://<app_name>.drupal.example.com/install.php?profile=standard&locale=ca\n"
          "By default this site will be accessible via http://<app_name>.drupal.example.com")
    ),
    'webalizer': (
        _("Webalizer"),
        'alias', ('%(app_path)s%(site_name)s',),
        _("This creates a Webalizer application under ~/webapps/<app_name>-<site_name>\n")
    ),
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
    'exec',  'passthru', 'shell_exec', 'system', 'proc_open', 'popen', 'curl_exec',
    'curl_multi_exec', 'show_source', 'pcntl_exec', 'proc_close',
    'proc_get_status', 'proc_nice', 'proc_terminate', 'ini_alter', 'virtual',
    'openlog', 'escapeshellcmd', 'escapeshellarg', 'dl'
])


WEBAPPS_WORDPRESSMU_BASE_URL = getattr(settings, 'WEBAPPS_WORDPRESSMU_BASE_URL',
    'http://blogs.example.com')


WEBAPPS_WORDPRESSMU_ADMIN_PASSWORD = getattr(settings, 'WEBAPPS_WORDPRESSMU_ADMIN_PASSWORD',
    'secret')





WEBAPPS_DOKUWIKIMU_TEMPLATE_PATH = setattr(settings, 'WEBAPPS_DOKUWIKIMU_TEMPLATE_PATH',
    '/home/httpd/htdocs/wikifarm/template.tar.gz')


WEBAPPS_DOKUWIKIMU_FARM_PATH = getattr(settings, 'WEBAPPS_DOKUWIKIMU_FARM_PATH',
    '/home/httpd/htdocs/wikifarm/farm')


WEBAPPS_DRUPAL_SITES_PATH = getattr(settings, 'WEBAPPS_DRUPAL_SITES_PATH',
    '/home/httpd/htdocs/drupal-mu/sites/%(app_name)s')


WEBAPPS_PHPFPM_POOL_PATH = getattr(settings, 'WEBAPPS_PHPFPM_POOL_PATH',
    '/etc/php5/fpm/pool.d')
