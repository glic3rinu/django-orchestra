from django.conf import settings
from django.utils.translation import ugettext_lazy as _


WEBAPPS_BASE_ROOT = getattr(settings, 'WEBAPPS_BASE_ROOT',
    '%(home)s/webapps/%(app_name)s/')


WEBAPPS_FPM_LISTEN = getattr(settings, 'WEBAPPS_FPM_LISTEN',
    # '127.0.0.1:9%(app_id)03d
    '/opt/php/5.4/socks/%(user)s-%(app_name)s.sock'
)

WEBAPPS_PHPFPM_POOL_PATH = getattr(settings, 'WEBAPPS_PHPFPM_POOL_PATH',
    '/etc/php5/fpm/pool.d/%(user)s-%(app_name)s.conf')


WEBAPPS_FCGID_WRAPPER_PATH = getattr(settings, 'WEBAPPS_FCGID_WRAPPER_PATH',
    '/home/httpd/fcgi-bin.d/%(user)s/%(app_name)s-wrapper')


WEBAPPS_FCGID_CMD_OPTIONS_PATH = getattr(settings, 'WEBAPPS_FCGID_CMD_OPTIONS_PATH',
    # Loaded by Apache
    '/etc/apache2/fcgid-conf/%(user)s-%(app_name)s.conf')


WEBAPPS_PHP_ERROR_LOG_PATH = getattr(settings, 'WEBAPPS_PHP_ERROR_LOG_PATH',
    '')


WEBAPPS_MERGE_PHP_WEBAPPS = getattr(settings, 'WEBAPPS_MERGE_PHP_WEBAPPS',
    # Combine all fcgid-wrappers/fpm-pools into one per account-php_version
    # to better control num processes per account and save memory
    False)


WEBAPPS_TYPES = getattr(settings, 'WEBAPPS_TYPES', (
    'orchestra.apps.webapps.types.php.PHPApp',
    'orchestra.apps.webapps.types.misc.StaticApp',
    'orchestra.apps.webapps.types.misc.WebalizerApp',
    'orchestra.apps.webapps.types.saas.WordPressMuApp',
    'orchestra.apps.webapps.types.saas.DokuWikiMuApp',
    'orchestra.apps.webapps.types.saas.DrupalMuApp',
    'orchestra.apps.webapps.types.misc.SymbolicLinkApp',
    'orchestra.apps.webapps.types.wordpress.WordPressApp',
))


WEBAPPS_PHP_VERSIONS = getattr(settings, 'WEBAPPS_PHP_VERSIONS', (
    # Execution modle choose by ending -fpm or -cgi
    ('5.4-fpm', 'PHP 5.4 FPM'),
    ('5.4-cgi', 'PHP 5.4 FCGID'),
    ('5.3-cgi', 'PHP 5.3 FCGID'),
    ('5.2-cgi', 'PHP 5.2 FCGID'),
    ('4-cgi', 'PHP 4 FCGID'),
))


WEBAPPS_DEFAULT_PHP_VERSION = getattr(settings, 'WEBAPPS_DEFAULT_PHP_VERSION',
    '5.4-cgi')


WEBAPPS_PHP_CGI_BINARY_PATH = getattr(settings, 'WEBAPPS_PHP_CGI_BINARY_PATH',
    # Path of the cgi binary used by fcgid
    '/usr/bin/php%(php_version_number)s-cgi')


WEBAPPS_PHP_CGI_RC_DIR = getattr(settings, 'WEBAPPS_PHP_CGI_RC_DIR',
    # Path to php.ini
    '/etc/php%(php_version_number)s/cgi/')


WEBAPPS_PHP_CGI_INI_SCAN_DIR = getattr(settings, 'WEBAPPS_PHP_CGI_INI_SCAN_DIR',
    # Path to php.ini
    '/etc/php%(php_version_number)s/cgi/conf.d')



WEBAPPS_UNDER_CONSTRUCTION_PATH = getattr(settings, 'WEBAPPS_UNDER_CONSTRUCTION_PATH',
    # Server-side path where a under construction stock page is
    # '/var/www/undercontruction/index.html',
    '')

#WEBAPPS_TYPES_OVERRIDE = getattr(settings, 'WEBAPPS_TYPES_OVERRIDE', {})
#for webapp_type, value in WEBAPPS_TYPES_OVERRIDE.iteritems():
#    if value is None:
#        WEBAPPS_TYPES.pop(webapp_type, None)
#    else:
#        WEBAPPS_TYPES[webapp_type] = value


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
    'orchestra.apps.webapps.options.PublicRoot',
    'orchestra.apps.webapps.options.Timeout',
    'orchestra.apps.webapps.options.Processes',
    'orchestra.apps.webapps.options.PHPEnabledFunctions',
    'orchestra.apps.webapps.options.PHPAllowURLInclude',
    'orchestra.apps.webapps.options.PHPAllowURLFopen',
    'orchestra.apps.webapps.options.PHPAutoAppendFile',
    'orchestra.apps.webapps.options.PHPAutoPrependFile',
    'orchestra.apps.webapps.options.PHPDateTimeZone',
    'orchestra.apps.webapps.options.PHPDefaultSocketTimeout',
    'orchestra.apps.webapps.options.PHPDisplayErrors',
    'orchestra.apps.webapps.options.PHPExtension',
    'orchestra.apps.webapps.options.PHPMagicQuotesGPC',
    'orchestra.apps.webapps.options.PHPMagicQuotesRuntime',
    'orchestra.apps.webapps.options.PHPMaginQuotesSybase',
    'orchestra.apps.webapps.options.PHPMaxExecutonTime',
    'orchestra.apps.webapps.options.PHPMaxInputTime',
    'orchestra.apps.webapps.options.PHPMaxInputVars',
    'orchestra.apps.webapps.options.PHPMemoryLimit',
    'orchestra.apps.webapps.options.PHPMySQLConnectTimeout',
    'orchestra.apps.webapps.options.PHPOutputBuffering',
    'orchestra.apps.webapps.options.PHPRegisterGlobals',
    'orchestra.apps.webapps.options.PHPPostMaxSize',
    'orchestra.apps.webapps.options.PHPSendmailPath',
    'orchestra.apps.webapps.options.PHPSessionBugCompatWarn',
    'orchestra.apps.webapps.options.PHPSessionAutoStart',
    'orchestra.apps.webapps.options.PHPSafeMode',
    'orchestra.apps.webapps.options.PHPSuhosinPostMaxVars',
    'orchestra.apps.webapps.options.PHPSuhosinGetMaxVars',
    'orchestra.apps.webapps.options.PHPSuhosinRequestMaxVars',
    'orchestra.apps.webapps.options.PHPSuhosinSessionEncrypt',
    'orchestra.apps.webapps.options.PHPSuhosinSimulation',
    'orchestra.apps.webapps.options.PHPSuhosinExecutorIncludeWhitelist',
    'orchestra.apps.webapps.options.PHPUploadMaxFileSize',
    'orchestra.apps.webapps.options.PHPZendExtension',
))


WEBAPPS_WORDPRESSMU_ADMIN_PASSWORD = getattr(settings, 'WEBAPPS_WORDPRESSMU_ADMIN_PASSWORD',
    'secret')

WEBAPPS_WORDPRESSMU_BASE_URL = getattr(settings, 'WEBAPPS_WORDPRESSMU_BASE_URL',
    'http://blogs.orchestra.lan/')

WEBAPPS_WORDPRESSMU_LISTEN = getattr(settings, 'WEBAPPS_WORDPRESSMU_LISTEN',
    '/opt/php/5.4/socks/wordpress-mu.sock'
)


WEBAPPS_DOKUWIKIMU_TEMPLATE_PATH = getattr(settings, 'WEBAPPS_DOKUWIKIMU_TEMPLATE_PATH',
    '/home/httpd/htdocs/wikifarm/template.tar.gz')

WEBAPPS_DOKUWIKIMU_FARM_PATH = getattr(settings, 'WEBAPPS_DOKUWIKIMU_FARM_PATH',
    '/home/httpd/htdocs/wikifarm/farm')

WEBAPPS_DOKUWIKIMU_LISTEN = getattr(settings, 'WEBAPPS_DOKUWIKIMU_LISTEN',
    '/opt/php/5.4/socks/dokuwiki-mu.sock'
)


WEBAPPS_DRUPALMU_SITES_PATH = getattr(settings, 'WEBAPPS_DRUPALMU_SITES_PATH',
    '/home/httpd/htdocs/drupal-mu/sites/%(site_name)s')

WEBAPPS_DRUPALMU_LISTEN = getattr(settings, 'WEBAPPS_DRUPALMU_LISTEN',
    '/opt/php/5.4/socks/drupal-mu.sock'
)


WEBAPPS_MOODLEMU_LISTEN = getattr(settings, 'WEBAPPS_MOODLEMU_LISTEN',
    '/opt/php/5.4/socks/moodle-mu.sock'
)


WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST = getattr(settings, 'WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST',
    'mysql.orchestra.lan')
