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
    '/home/httpd/fcgid/%(user)s/%(app_name)s-wrapper')


WEBAPPS_TYPES = getattr(settings, 'WEBAPPS_TYPES', (
    'orchestra.apps.webapps.types.Php55App',
    'orchestra.apps.webapps.types.Php52App',
    'orchestra.apps.webapps.types.Php4App',
    'orchestra.apps.webapps.types.StaticApp',
    'orchestra.apps.webapps.types.WebalizerApp',
    'orchestra.apps.webapps.types.WordPressMuApp',
    'orchestra.apps.webapps.types.DokuWikiMuApp',
    'orchestra.apps.webapps.types.DrupalMuApp',
    'orchestra.apps.webapps.types.SymbolicLinkApp',
    'orchestra.apps.webapps.types.WordPressApp',
))


#WEBAPPS_TYPES_OVERRIDE = getattr(settings, 'WEBAPPS_TYPES_OVERRIDE', {})
#for webapp_type, value in WEBAPPS_TYPES_OVERRIDE.iteritems():
#    if value is None:
#        WEBAPPS_TYPES.pop(webapp_type, None)
#    else:
#        WEBAPPS_TYPES[webapp_type] = value


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


WEBAPPS_ENABLED_OPTIONS = getattr(settings, 'WEBAPPS_ENABLED_OPTIONS', (
    'orchestra.apps.webapps.options.public_root',
    'orchestra.apps.webapps.options.timeout',
    'orchestra.apps.webapps.options.processes',
    'orchestra.apps.webapps.options.php_enabled_functions',
    'orchestra.apps.webapps.options.php_allow_url_include',
    'orchestra.apps.webapps.options.php_allow_url_fopen',
    'orchestra.apps.webapps.options.php_auto_append_file',
    'orchestra.apps.webapps.options.php_auto_prepend_file',
    'orchestra.apps.webapps.options.php_date_timezone',
    'orchestra.apps.webapps.options.php_default_socket_timeout',
    'orchestra.apps.webapps.options.php_display_errors',
    'orchestra.apps.webapps.options.php_extension',
    'orchestra.apps.webapps.options.php_magic_quotes_gpc',
    'orchestra.apps.webapps.options.php_magic_quotes_runtime',
    'orchestra.apps.webapps.options.php_magic_quotes_sybase',
    'orchestra.apps.webapps.options.php_max_execution_time',
    'orchestra.apps.webapps.options.php_max_input_time',
    'orchestra.apps.webapps.options.php_max_input_vars',
    'orchestra.apps.webapps.options.php_memory_limit',
    'orchestra.apps.webapps.options.php_mysql_connect_timeout',
    'orchestra.apps.webapps.options.php_output_buffering',
    'orchestra.apps.webapps.options.php_register_globals',
    'orchestra.apps.webapps.options.php_post_max_size',
    'orchestra.apps.webapps.options.php_sendmail_path',
    'orchestra.apps.webapps.options.php_session_bug_compat_warn',
    'orchestra.apps.webapps.options.php_session_auto_start',
    'orchestra.apps.webapps.options.php_safe_mode',
    'orchestra.apps.webapps.options.php_suhosin_post_max_vars',
    'orchestra.apps.webapps.options.php_suhosin_get_max_vars',
    'orchestra.apps.webapps.options.php_suhosin_request_max_vars',
    'orchestra.apps.webapps.options.php_suhosin_session_encrypt',
    'orchestra.apps.webapps.options.php_suhosin_simulation',
    'orchestra.apps.webapps.options.php_suhosin_executor_include_whitelist',
    'orchestra.apps.webapps.options.php_upload_max_filesize',
    'orchestra.apps.webapps.options.php_zend_extension',
))


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


WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST = getattr(settings, 'WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST',
    'mysql.orchestra.lan')
