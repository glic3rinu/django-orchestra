from django.conf import settings

from orchestra.settings import ORCHESTRA_BASE_DOMAIN


WEBAPPS_BASE_ROOT = getattr(settings, 'WEBAPPS_BASE_ROOT',
    '%(home)s/webapps/%(app_name)s/'
)


WEBAPPS_FPM_LISTEN = getattr(settings, 'WEBAPPS_FPM_LISTEN',
    # '127.0.0.1:9%(app_id)03d
    '/opt/php/5.4/socks/%(user)s-%(app_name)s.sock'
)

WEBAPPS_PHPFPM_POOL_PATH = getattr(settings, 'WEBAPPS_PHPFPM_POOL_PATH',
    '/etc/php5/fpm/pool.d/%(user)s-%(app_name)s.conf')


WEBAPPS_FCGID_WRAPPER_PATH = getattr(settings, 'WEBAPPS_FCGID_WRAPPER_PATH',
    # Inside SuExec Document root
    '/home/httpd/fcgi-bin.d/%(user)s/%(app_name)s-wrapper'
)


WEBAPPS_FCGID_CMD_OPTIONS_PATH = getattr(settings, 'WEBAPPS_FCGID_CMD_OPTIONS_PATH',
    # Loaded by Apache
    '/etc/apache2/fcgid-conf/%(user)s-%(app_name)s.conf'
)


# Greater or equal to your FcgidMaxRequestsPerProcess
# http://httpd.apache.org/mod_fcgid/mod/mod_fcgid.html#examples
WEBAPPS_PHP_MAX_REQUESTS = getattr(settings, 'WEBAPPS_PHP_MAX_REQUESTS',
    400
)


WEBAPPS_PHP_ERROR_LOG_PATH = getattr(settings, 'WEBAPPS_PHP_ERROR_LOG_PATH',
    ''
)


WEBAPPS_MERGE_PHP_WEBAPPS = getattr(settings, 'WEBAPPS_MERGE_PHP_WEBAPPS',
    # Combine all fcgid-wrappers/fpm-pools into one per account-php_version
    # to better control num processes per account and save memory
    False)


WEBAPPS_TYPES = getattr(settings, 'WEBAPPS_TYPES', (
    'orchestra.contrib.webapps.types.php.PHPApp',
    'orchestra.contrib.webapps.types.misc.StaticApp',
    'orchestra.contrib.webapps.types.misc.WebalizerApp',
    'orchestra.contrib.webapps.types.misc.SymbolicLinkApp',
    'orchestra.contrib.webapps.types.wordpress.WordPressApp',
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
    '5.4-cgi'
)


WEBAPPS_PHP_CGI_BINARY_PATH = getattr(settings, 'WEBAPPS_PHP_CGI_BINARY_PATH',
    # Path of the cgi binary used by fcgid
    '/usr/bin/php%(php_version_number)s-cgi'
)


WEBAPPS_PHP_CGI_RC_DIR = getattr(settings, 'WEBAPPS_PHP_CGI_RC_DIR',
    # Path to php.ini
    '/etc/php%(php_version_number)s/cgi/'
)


WEBAPPS_PHP_CGI_INI_SCAN_DIR = getattr(settings, 'WEBAPPS_PHP_CGI_INI_SCAN_DIR',
    # Path to php.ini
    '/etc/php%(php_version_number)s/cgi/conf.d'
)



WEBAPPS_UNDER_CONSTRUCTION_PATH = getattr(settings, 'WEBAPPS_UNDER_CONSTRUCTION_PATH',
    # Server-side path where a under construction stock page is
    # '/var/www/undercontruction/index.html',
    ''
)


#WEBAPPS_TYPES_OVERRIDE = getattr(settings, 'WEBAPPS_TYPES_OVERRIDE', {})
#for webapp_type, value in WEBAPPS_TYPES_OVERRIDE.items():
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
    'orchestra.contrib.webapps.options.PublicRoot',
    'orchestra.contrib.webapps.options.Timeout',
    'orchestra.contrib.webapps.options.Processes',
    'orchestra.contrib.webapps.options.PHPEnabledFunctions',
    'orchestra.contrib.webapps.options.PHPAllowURLInclude',
    'orchestra.contrib.webapps.options.PHPAllowURLFopen',
    'orchestra.contrib.webapps.options.PHPAutoAppendFile',
    'orchestra.contrib.webapps.options.PHPAutoPrependFile',
    'orchestra.contrib.webapps.options.PHPDateTimeZone',
    'orchestra.contrib.webapps.options.PHPDefaultSocketTimeout',
    'orchestra.contrib.webapps.options.PHPDisplayErrors',
    'orchestra.contrib.webapps.options.PHPExtension',
    'orchestra.contrib.webapps.options.PHPMagicQuotesGPC',
    'orchestra.contrib.webapps.options.PHPMagicQuotesRuntime',
    'orchestra.contrib.webapps.options.PHPMaginQuotesSybase',
    'orchestra.contrib.webapps.options.PHPMaxExecutonTime',
    'orchestra.contrib.webapps.options.PHPMaxInputTime',
    'orchestra.contrib.webapps.options.PHPMaxInputVars',
    'orchestra.contrib.webapps.options.PHPMemoryLimit',
    'orchestra.contrib.webapps.options.PHPMySQLConnectTimeout',
    'orchestra.contrib.webapps.options.PHPOutputBuffering',
    'orchestra.contrib.webapps.options.PHPRegisterGlobals',
    'orchestra.contrib.webapps.options.PHPPostMaxSize',
    'orchestra.contrib.webapps.options.PHPSendmailPath',
    'orchestra.contrib.webapps.options.PHPSessionBugCompatWarn',
    'orchestra.contrib.webapps.options.PHPSessionAutoStart',
    'orchestra.contrib.webapps.options.PHPSafeMode',
    'orchestra.contrib.webapps.options.PHPSuhosinPostMaxVars',
    'orchestra.contrib.webapps.options.PHPSuhosinGetMaxVars',
    'orchestra.contrib.webapps.options.PHPSuhosinRequestMaxVars',
    'orchestra.contrib.webapps.options.PHPSuhosinSessionEncrypt',
    'orchestra.contrib.webapps.options.PHPSuhosinSimulation',
    'orchestra.contrib.webapps.options.PHPSuhosinExecutorIncludeWhitelist',
    'orchestra.contrib.webapps.options.PHPUploadMaxFileSize',
    'orchestra.contrib.webapps.options.PHPZendExtension',
))


WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST = getattr(settings, 'WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST',
    'mysql.{}'.format(ORCHESTRA_BASE_DOMAIN)
)
