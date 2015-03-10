from django.conf import settings
from django.utils.translation import ugettext_lazy as _


WEBAPPS_BASE_ROOT = getattr(settings, 'WEBAPPS_BASE_ROOT', '{home}/webapps/{app_name}/')



WEBAPPS_FPM_LISTEN = getattr(settings, 'WEBAPPS_FPM_LISTEN',
    # '127.0.0.1:9{app_id:03d}
    '/opt/php/5.4/socks/{user}-{app_name}.sock'
)

WEBAPPS_FPM_START_PORT = getattr(settings, 'WEBAPPS_FPM_START_PORT', 10000)


WEBAPPS_PHPFPM_POOL_PATH = getattr(settings, 'WEBAPPS_PHPFPM_POOL_PATH',
    '/etc/php5/fpm/pool.d/{user}-{app_name}.conf')


WEBAPPS_FCGID_PATH = getattr(settings, 'WEBAPPS_FCGID_PATH',
    '/home/httpd/fcgid/{user}/{app_name}-wrapper')


WEBAPPS_TYPES = getattr(settings, 'WEBAPPS_TYPES', (
    'orchestra.apps.webapps.types.PHP54App',
    'orchestra.apps.webapps.types.PHP52App',
    'orchestra.apps.webapps.types.PHP4App',
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
    'orchestra.apps.webapps.options.PublicRoot',
    'orchestra.apps.webapps.options.DirectoryProtection',
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
    'orchestra.apps.webapps.options.PHPPostMaxSize',
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
    '/home/httpd/htdocs/drupal-mu/sites/{site_name}')

WEBAPPS_DRUPALMU_LISTEN = getattr(settings, 'WEBAPPS_DRUPALMU_LISTEN',
    '/opt/php/5.4/socks/drupal-mu.sock'
)


WEBAPPS_MOODLEMU_LISTEN = getattr(settings, 'WEBAPPS_MOODLEMU_LISTEN',
    '/opt/php/5.4/socks/moodle-mu.sock'
)


WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST = getattr(settings, 'WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST',
    'mysql.orchestra.lan')
