from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra.utils.python import import_class

from . import settings


class AppOption(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.verbose_name = kwargs.pop('verbose_name', name)
        self.help_text = kwargs.pop('help_text', '')
        for k,v in kwargs.iteritems():
            setattr(self, k, v)
    
    def validate(self, webapp):
        if self.regex and not re.match(self.regex, webapp.value):
            raise ValidationError({
                'value': ValidationError(_("'%(value)s' does not match %(regex)s."),
                    params={
                        'value': webapp.value,
                        'regex': self.regex
                    }),
            })


public_root = AppOption('public-root',
    verbose_name=_("Public root"),
    help_text=_("Document root relative to webapps/&lt;webapp&gt;/"),
    regex=r'[^ ]+'
)

timeout = AppOption('timeout',
    # FCGID FcgidIOTimeout
    # FPM pm.request_terminate_timeout
    # PHP max_execution_time ini
    verbose_name=_("Process timeout"),
    help_text=_("Maximum time in seconds allowed for a request to complete (a number between 0 and 999)."),
    regex=r'^[0-9]{1,3}$',
)

processes = AppOption('processes',
    # FCGID MaxProcesses
    # FPM pm.max_children
    verbose_name=_("Number of processes"),
    help_text=_("Maximum number of children that can be alive at the same time (a number between 0 and 9)."),
    regex=r'^[0-9]$',
)

php_enabled_functions = AppOption('php-enabled_functions',
    verbose_name=_("Enabled functions"),
    help_text = ' '.join(settings.WEBAPPS_PHP_DISABLED_FUNCTIONS),
    regex=r'^[\w\.,-]+$'
)

php_allow_url_include = AppOption('PHP-allow_url_include',
    verbose_name=_("Allow URL include"),
    help_text=_("Allows the use of URL-aware fopen wrappers with include, include_once, require, "
                "require_once (On or Off)."),
    regex=r'^(On|Off|on|off)$'
)

php_allow_url_fopen = AppOption('PHP-allow_url_fopen',
    verbose_name=_("Allow URL fopen"),
    help_text=_("Enables the URL-aware fopen wrappers that enable accessing URL object like files (On or Off)."),
    regex=r'^(On|Off|on|off)$'
)

php_auto_append_file = AppOption('PHP-auto_append_file',
    verbose_name=_("Auto append file"),
    help_text=_("Specifies the name of a file that is automatically parsed after the main file."),
    regex=r'^[\w\.,-/]+$'
)

php_auto_prepend_file = AppOption('PHP-auto_prepend_file',
    verbose_name=_("Auto prepend file"),
    help_text=_("Specifies the name of a file that is automatically parsed before the main file."),
    regex=r'^[\w\.,-/]+$'
)

php_date_timezone = AppOption('PHP-date.timezone',
    verbose_name=_("date.timezone"),
    help_text=_("Sets the default timezone used by all date/time functions (Timezone string 'Europe/London')."),
    regex=r'^\w+/\w+$'
)

php_default_socket_timeout = AppOption('PHP-default_socket_timeout',
    verbose_name=_("Default socket timeout"),
    help_text=_("Number between 0 and 999."),
    regex=r'^[0-9]{1,3}$'
)

php_display_errors = AppOption('PHP-display_errors',
    verbose_name=_("Display errors"),
    help_text=_("Determines whether errors should be printed to the screen as part of the output or "
                "if they should be hidden from the user (On or Off)."),
    regex=r'^(On|Off|on|off)$'
)

php_extension = AppOption('PHP-extension',
    verbose_name=_("Extension"),
    regex=r'^[^ ]+$'
)

php_magic_quotes_gpc = AppOption('PHP-magic_quotes_gpc',
    verbose_name=_("Magic quotes GPC"),
    help_text=_("Sets the magic_quotes state for GPC (Get/Post/Cookie) operations (On or Off) "
                "<b>DEPRECATED as of PHP 5.3.0</b>."),
    regex=r'^(On|Off|on|off)$',
    deprecated=5.3
)

php_magic_quotes_runtime = AppOption('PHP-magic_quotes_runtime',
    verbose_name=_("Magic quotes runtime"),
    help_text=_("Functions that return data from any sort of external source will have quotes escaped "
                "with a backslash (On or Off) <b>DEPRECATED as of PHP 5.3.0</b>."),
    regex=r'^(On|Off|on|off)$',
    deprecated=5.3
)

php_magic_quotes_sybase = AppOption('PHP-magic_quotes_sybase',
    verbose_name=_("Magic quotes sybase"),
    help_text=_("Single-quote is escaped with a single-quote instead of a backslash (On or Off)."),
    regex=r'^(On|Off|on|off)$'
)

php_max_execution_time = AppOption('PHP-max_execution_time',
    verbose_name=_("Max execution time"),
    help_text=_("Maximum time in seconds a script is allowed to run before it is terminated by "
                "the parser (Integer between 0 and 999)."),
    regex=r'^[0-9]{1,3}$'
)

php_max_input_time = AppOption('PHP-max_input_time',
    verbose_name=_("Max input time"),
    help_text=_("Maximum time in seconds a script is allowed to parse input data, like POST and GET "
                "(Integer between 0 and 999)."),
    regex=r'^[0-9]{1,3}$'
)

php_max_input_vars = AppOption('PHP-max_input_vars',
    verbose_name=_("Max input vars"),
    help_text=_("How many input variables may be accepted (limit is applied to $_GET, $_POST "
                "and $_COOKIE superglobal separately) (Integer between 0 and 9999)."),
    regex=r'^[0-9]{1,4}$'
)

php_memory_limit = AppOption('PHP-memory_limit',
    verbose_name=_("Memory limit"),
    help_text=_("This sets the maximum amount of memory in bytes that a script is allowed to allocate "
                "(Value between 0M and 999M)."),
    regex=r'^[0-9]{1,3}M$'
)

php_mysql_connect_timeout = AppOption('PHP-mysql.connect_timeout',
    verbose_name=_("Mysql connect timeout"),
    help_text=_("Number between 0 and 999."),
    regex=r'^([0-9]){1,3}$'
)

php_output_buffering = AppOption('PHP-output_buffering',
    verbose_name=_("Output buffering"),
    help_text=_("Turn on output buffering (On or Off)."),
    regex=r'^(On|Off|on|off)$'
)

php_register_globals = AppOption('PHP-register_globals',
    verbose_name=_("Register globals"),
    help_text=_("Whether or not to register the EGPCS (Environment, GET, POST, Cookie, Server) "
                "variables as global variables (On or Off)."),
    regex=r'^(On|Off|on|off)$'
)

php_post_max_size = AppOption('PHP-post_max_size',
    verbose_name=_("Post max size"),
    help_text=_("Sets max size of post data allowed (Value between 0M and 999M)."),
    regex=r'^[0-9]{1,3}M$'
)

php_sendmail_path = AppOption('PHP-sendmail_path',
    verbose_name=_("sendmail_path"),
    help_text=_("Where the sendmail program can be found."),
    regex=r'^[^ ]+$'
)

php_session_bug_compat_warn = AppOption('PHP-session.bug_compat_warn',
    verbose_name=_("session.bug_compat_warn"),
    help_text=_("Enables an PHP bug on session initialization for legacy behaviour (On or Off)."),
    regex=r'^(On|Off|on|off)$'
)

php_session_auto_start = AppOption('PHP-session.auto_start',
    verbose_name=_("session.auto_start"),
    help_text=_("Specifies whether the session module starts a session automatically on request "
                "startup (On or Off)."),
    regex=r'^(On|Off|on|off)$'
)
php_safe_mode = AppOption('PHP-safe_mode',
    verbose_name=_("Safe mode"),
    help_text=_("Whether to enable PHP's safe mode (On or Off) <b>DEPRECATED as of PHP 5.3.0</b>"),
    regex=r'^(On|Off|on|off)$',
    deprecated=5.3
)
php_suhosin_post_max_vars = AppOption('PHP-suhosin.post.max_vars',
    verbose_name=_("Suhosin POST max vars"),
    help_text=_("Number between 0 and 9999."),
    regex=r'^[0-9]{1,4}$'
)
php_suhosin_get_max_vars = AppOption('PHP-suhosin.get.max_vars',
    verbose_name=_("Suhosin GET max vars"),
    help_text=_("Number between 0 and 9999."),
    regex=r'^[0-9]{1,4}$'
)
php_suhosin_request_max_vars = AppOption('PHP-suhosin.request.max_vars',
    verbose_name=_("Suhosin request max vars"),
    help_text=_("Number between 0 and 9999."),
    regex=r'^[0-9]{1,4}$'
)
php_suhosin_session_encrypt = AppOption('PHP-suhosin.session.encrypt',
    verbose_name=_("suhosin.session.encrypt"),
    help_text=_("On or Off"),
    regex=r'^(On|Off|on|off)$'
)
php_suhosin_simulation = AppOption('PHP-suhosin.simulation',
    verbose_name=_("Suhosin simulation"),
    help_text=_("On or Off"),
    regex=r'^(On|Off|on|off)$'
)
php_suhosin_executor_include_whitelist = AppOption('PHP-suhosin.executor.include.whitelist',
    verbose_name=_("suhosin.executor.include.whitelist"),
    regex=r'.*$'
)
php_upload_max_filesize = AppOption('PHP-upload_max_filesize',
    verbose_name=_("upload_max_filesize"),
    help_text=_("Value between 0M and 999M."),
    regex=r'^[0-9]{1,3}M$'
)
php_zend_extension = AppOption('PHP-post_max_size',
    verbose_name=_("zend_extension"),
    regex=r'^[^ ]+$'
)


filesystem = [
    public_root,
]

process = [
    timeout,
    processes,
]

php = [
    php_enabled_functions,
    php_allow_url_include,
    php_allow_url_fopen,
    php_auto_append_file,
    php_auto_prepend_file,
    php_date_timezone,
    php_default_socket_timeout,
    php_display_errors,
    php_extension,
    php_magic_quotes_gpc,
    php_magic_quotes_runtime,
    php_magic_quotes_sybase,
    php_max_execution_time,
    php_max_input_time,
    php_max_input_vars,
    php_memory_limit,
    php_mysql_connect_timeout,
    php_output_buffering,
    php_register_globals,
    php_post_max_size,
    php_sendmail_path,
    php_session_bug_compat_warn,
    php_session_auto_start,
    php_safe_mode,
    php_suhosin_post_max_vars,
    php_suhosin_get_max_vars,
    php_suhosin_request_max_vars,
    php_suhosin_session_encrypt,
    php_suhosin_simulation,
    php_suhosin_executor_include_whitelist,
    php_upload_max_filesize,
    php_zend_extension,
]


_enabled = None

def get_enabled():
    global _enabled
    if _enabled is None:
        from . import settings
        _enabled = {}
        for op in settings.WEBAPPS_ENABLED_OPTIONS:
            op = import_class(op)
            _enabled[op.name] = op
    return _enabled
