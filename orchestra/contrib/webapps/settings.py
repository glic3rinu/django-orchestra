from orchestra.settings import ORCHESTRA_BASE_DOMAIN, Setting

from .. import webapps


_names = ('home', 'user', 'group', 'app_type', 'app_name', 'app_type', 'app_id')
_php_names = _names + ('php_version', 'php_version_number',)
_python_names = _names + ('python_version', 'python_version_number',)


WEBAPPS_BASE_DIR = Setting('WEBAPPS_BASE_DIR',
    '%(home)s/webapps/%(app_name)s',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_names),
    validators=[Setting.string_format_validator(_names)],
)


WEBAPPS_FPM_LISTEN = Setting('WEBAPPS_FPM_LISTEN',
    '/opt/php/5.4/socks/%(user)s-%(app_name)s.sock',
    help_text=("TCP socket example: <tt>127.0.0.1:9%(app_id)03d</tt><br>"
               "Available fromat names: <tt>{}</tt>").format(', '.join(_php_names)),
    validators=[Setting.string_format_validator(_php_names)],
)


WEBAPPS_FPM_DEFAULT_MAX_CHILDREN = Setting('WEBAPPS_FPM_DEFAULT_MAX_CHILDREN',
    3
)


WEBAPPS_PHPFPM_POOL_PATH = Setting('WEBAPPS_PHPFPM_POOL_PATH',
    '/etc/php5/fpm/pool.d/%(user)s-%(app_name)s.conf',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_php_names),
    validators=[Setting.string_format_validator(_php_names)],
)


WEBAPPS_FCGID_WRAPPER_PATH = Setting('WEBAPPS_FCGID_WRAPPER_PATH',
    '/home/httpd/fcgi-bin.d/%(user)s/%(app_name)s-wrapper',
    validators=[Setting.string_format_validator(_php_names)],
    help_text=("Inside SuExec Document root.<br>"
               "Make sure all account wrappers are in the same DIR.<br>"
               "Available fromat names: <tt>%s</tt>") % ', '.join(_php_names),
)


WEBAPPS_FCGID_CMD_OPTIONS_PATH = Setting('WEBAPPS_FCGID_CMD_OPTIONS_PATH',
    '/etc/apache2/fcgid-conf/%(user)s-%(app_name)s.conf',
    validators=[Setting.string_format_validator(_php_names)],
    help_text="Loaded by Apache. Available fromat names: <tt>%s</tt>" % ', '.join(_php_names),
)


WEBAPPS_PHP_MAX_REQUESTS = Setting('WEBAPPS_PHP_MAX_REQUESTS',
    400,
    help_text='Greater or equal to your <a href="http://httpd.apache.org/mod_fcgid/mod/mod_fcgid.html#examples">FcgidMaxRequestsPerProcess</a>'
)


WEBAPPS_PHP_ERROR_LOG_PATH = Setting('WEBAPPS_PHP_ERROR_LOG_PATH',
    ''
)


WEBAPPS_MERGE_PHP_WEBAPPS = Setting('WEBAPPS_MERGE_PHP_WEBAPPS',
    False,
    help_text=("Combine all fcgid-wrappers/fpm-pools into one per account-php_version "
               "to better control num processes per account and save memory")
)

WEBAPPS_TYPES = Setting('WEBAPPS_TYPES', (
        'orchestra.contrib.webapps.types.php.PHPApp',
        'orchestra.contrib.webapps.types.misc.StaticApp',
        'orchestra.contrib.webapps.types.misc.WebalizerApp',
        'orchestra.contrib.webapps.types.misc.SymbolicLinkApp',
        'orchestra.contrib.webapps.types.wordpress.WordPressApp',
        'orchestra.contrib.webapps.types.python.PythonApp',
    ),
    # lazy loading
    choices=lambda : ((t.get_class_path(), t.get_class_path()) for t in webapps.types.AppType.get_plugins()),
    multiple=True,
)


WEBAPPS_PHP_VERSIONS = Setting('WEBAPPS_PHP_VERSIONS', (
        ('5.4-fpm', 'PHP 5.4 FPM'),
        ('5.4-cgi', 'PHP 5.4 FCGID'),
        ('5.3-cgi', 'PHP 5.3 FCGID'),
        ('5.2-cgi', 'PHP 5.2 FCGID'),
        ('4-cgi', 'PHP 4 FCGID'),
    ),
    help_text="Execution modle choose by ending -fpm or -cgi.",
    validators=[Setting.validate_choices]
)


WEBAPPS_DEFAULT_PHP_VERSION = Setting('WEBAPPS_DEFAULT_PHP_VERSION',
    '5.4-cgi',
    choices=WEBAPPS_PHP_VERSIONS
)


WEBAPPS_PHP_CGI_BINARY_PATH = Setting('WEBAPPS_PHP_CGI_BINARY_PATH',
    '/usr/bin/php%(php_version_number)s-cgi',
    help_text="Path of the cgi binary used by fcgid. Available fromat names: <tt>%s</tt>" % ', '.join(_php_names),
    validators=[Setting.string_format_validator(_php_names)],
)


WEBAPPS_PHP_CGI_RC_DIR = Setting('WEBAPPS_PHP_CGI_RC_DIR',
    '/etc/php%(php_version_number)s/cgi/',
    help_text="Path to php.ini. Available fromat names: <tt>%s</tt>" % ', '.join(_php_names),
    validators=[Setting.string_format_validator(_php_names)],
)


WEBAPPS_PHP_CGI_INI_SCAN_DIR = Setting('WEBAPPS_PHP_CGI_INI_SCAN_DIR',
    '/etc/php%(php_version_number)s/cgi/conf.d',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_php_names),
    validators=[Setting.string_format_validator(_php_names)],
)


WEBAPPS_PYTHON_VERSIONS = Setting('WEBAPPS_PYTHON_VERSIONS',
    (
        ('3.4-uwsgi', 'Python 3.4 uWSGI'),
        ('2.7-uwsgi', 'Python 2.7 uWSGI'),
    ),
    validators=[Setting.validate_choices]
)


WEBAPPS_DEFAULT_PYTHON_VERSION = Setting('WEBAPPS_DEFAULT_PYTHON_VERSION',
    '3.4-uwsgi',
    choices=WEBAPPS_PYTHON_VERSIONS

)


WEBAPPS_UWSGI_SOCKET = Setting('WEBAPPS_UWSGI_SOCKET',
    '/var/run/uwsgi/app/%(app_name)s/socket',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_python_names),
    validators=[Setting.string_format_validator(_python_names)],
)


WEBAPPS_UWSGI_BASE_DIR = Setting('WEBAPPS_UWSGI_BASE_DIR',
    '/etc/uwsgi/'
)


WEBAPPS_PYTHON_MAX_REQUESTS = Setting('WEBAPPS_PYTHON_MAX_REQUESTS',
    500
)


WEBAPPS_PYTHON_DEFAULT_MAX_WORKERS = Setting('WEBAPPS_PYTHON_DEFAULT_MAX_WORKERS',
    3
)


WEBAPPS_PYTHON_DEFAULT_TIMEOUT = Setting('WEBAPPS_PYTHON_DEFAULT_TIMEOUT',
    30
)


WEBAPPS_UNDER_CONSTRUCTION_PATH = Setting('WEBAPPS_UNDER_CONSTRUCTION_PATH', '',
    help_text=("Server-side path where a under construction stock page is "
               "'/var/www/undercontruction/index.html'")
)


#WEBAPPS_TYPES_OVERRIDE = getattr(settings, 'WEBAPPS_TYPES_OVERRIDE', {})
#for webapp_type, value in WEBAPPS_TYPES_OVERRIDE.items():
#    if value is None:
#        WEBAPPS_TYPES.pop(webapp_type, None)
#    else:
#        WEBAPPS_TYPES[webapp_type] = value



WEBAPPS_PHP_DISABLED_FUNCTIONS = Setting('WEBAPPS_PHP_DISABLED_FUNCTION', (
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
))


WEBAPPS_ENABLED_OPTIONS = Setting('WEBAPPS_ENABLED_OPTIONS', (
        'orchestra.contrib.webapps.options.PublicRoot',
        'orchestra.contrib.webapps.options.Timeout',
        'orchestra.contrib.webapps.options.Processes',
        'orchestra.contrib.webapps.options.PHPEnableFunctions',
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
    ),
    # lazy loading
    choices=lambda : ((o.get_class_path(), o.get_class_path()) for o in webapps.options.AppOption.get_plugins()),
    multiple=True,
)


WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST = Setting('WEBAPPS_DEFAULT_MYSQL_DATABASE_HOST',
    'mysql.{}'.format(ORCHESTRA_BASE_DOMAIN),
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default.",
)


WEBAPPS_MOVE_ON_DELETE_PATH = Setting('WEBAPPS_MOVE_ON_DELETE_PATH',
    ''
)
