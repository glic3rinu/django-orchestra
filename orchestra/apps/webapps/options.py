from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra.plugins import Plugin
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from . import settings


class AppOption(Plugin):
    PHP = 'PHP'
    PROCESS = 'Process'
    FILESYSTEM = 'FileSystem'
    
    help_text = ""
    group = None
    
    @classmethod
    @cached
    def get_plugins(cls):
        plugins = []
        for cls in settings.WEBAPPS_ENABLED_OPTIONS:
            plugins.append(import_class(cls))
        return plugins
    
    @classmethod
    @cached
    def get_option_groups(cls):
        groups = {}
        for opt in cls.get_plugins():
            try:
                groups[opt.group].append(opt)
            except KeyError:
                groups[opt.group] = [opt]
        return groups
    
    def validate(self, option):
        if self.regex and not re.match(self.regex, option.value):
            raise ValidationError({
                'value': ValidationError(_("'%(value)s' does not match %(regex)s."),
                    params={
                        'value': option.value,
                        'regex': self.regex
                    }),
            })


class PublicRoot(AppOption):
    name = 'public-root'
    verbose_name = _("Public root")
    help_text = _("Document root relative to webapps/&lt;webapp&gt;/")
    regex = r'[^ ]+'
    group = AppOption.FILESYSTEM


class DirectoryProtection(AppOption):
    name = 'directory-protection'
    verbose_name = _("Directory protection")
    help_text = _("Space separated ...")
    regex = r'^([\w/_]+)\s+(\".*\")\s+([\w/_\.]+)$'
    group = AppOption.FILESYSTEM



class Timeout(AppOption):
    name = 'timeout'
    # FCGID FcgidIOTimeout
    # FPM pm.request_terminate_timeout
    # PHP max_execution_time ini
    verbose_name = _("Process timeout")
    help_text = _("Maximum time in seconds allowed for a request to complete (a number between 0 and 999).")
    regex = r'^[0-9]{1,3}$'
    group = AppOption.PROCESS


class Processes(AppOption):
    name = 'processes'
    # FCGID MaxProcesses
    # FPM pm.max_children
    verbose_name=_("Number of processes")
    help_text=_("Maximum number of children that can be alive at the same time (a number between 0 and 9).")
    regex=r'^[0-9]$'
    group = AppOption.PROCESS


class PHPEnabledFunctions(AppOption):
    name = 'enabled_functions'
    verbose_name=_("Enabled functions")
    help_text = ' '.join(settings.WEBAPPS_PHP_DISABLED_FUNCTIONS)
    regex=r'^[\w\.,-]+$'
    group = AppOption.PHP


class PHPAllowURLInclude(AppOption):
    name = 'allow_url_include'
    verbose_name=_("Allow URL include")
    help_text=_("Allows the use of URL-aware fopen wrappers with include, include_once, require, "
                "require_once (On or Off).")
    regex=r'^(On|Off|on|off)$'
    group = AppOption.PHP


class PHPAllowURLFopen(AppOption):
    name = 'allow_url_fopen'
    verbose_name=_("Allow URL fopen")
    help_text=_("Enables the URL-aware fopen wrappers that enable accessing URL object like files (On or Off).")
    regex=r'^(On|Off|on|off)$'
    group = AppOption.PHP


class PHPAutoAppendFile(AppOption):
    name = 'auto_append_file'
    verbose_name=_("Auto append file")
    help_text=_("Specifies the name of a file that is automatically parsed after the main file.")
    regex=r'^[\w\.,-/]+$'
    group = AppOption.PHP


class PHPAutoPrependFile(AppOption):
    name = 'auto_prepend_file'
    verbose_name=_("Auto prepend file")
    help_text=_("Specifies the name of a file that is automatically parsed before the main file.")
    regex=r'^[\w\.,-/]+$'
    group = AppOption.PHP


class PHPDateTimeZone(AppOption):
    name = 'date.timezone'
    verbose_name=_("date.timezone")
    help_text=_("Sets the default timezone used by all date/time functions (Timezone string 'Europe/London').")
    regex=r'^\w+/\w+$'
    group = AppOption.PHP


class PHPDefaultSocketTimeout(AppOption):
    name = 'default_socket_timeout'
    verbose_name=_("Default socket timeout")
    help_text=_("Number between 0 and 999.")
    regex=r'^[0-9]{1,3}$'
    group = AppOption.PHP


class PHPDisplayErrors(AppOption):
    name = 'display_errors'
    verbose_name=_("Display errors")
    help_text=_("Determines whether errors should be printed to the screen as part of the output or "
                "if they should be hidden from the user (On or Off).")
    regex=r'^(On|Off|on|off)$'
    group = AppOption.PHP


class PHPExtension(AppOption):
    name = 'extension'
    verbose_name=_("Extension")
    regex=r'^[^ ]+$'
    group = AppOption.PHP


class PHPMagicQuotesGPC(AppOption):
    name = 'magic_quotes_gpc'
    verbose_name=_("Magic quotes GPC")
    help_text=_("Sets the magic_quotes state for GPC (Get/Post/Cookie) operations (On or Off) "
                "<b>DEPRECATED as of PHP 5.3.0</b>.")
    regex=r'^(On|Off|on|off)$'
    deprecated=5.3
    group = AppOption.PHP


class PHPMagicQuotesRuntime(AppOption):
    name = 'magic_quotes_runtime'
    verbose_name=_("Magic quotes runtime")
    help_text=_("Functions that return data from any sort of external source will have quotes escaped "
                "with a backslash (On or Off) <b>DEPRECATED as of PHP 5.3.0</b>.")
    regex=r'^(On|Off|on|off)$'
    deprecated=5.3
    group = AppOption.PHP


class PHPMaginQuotesSybase(AppOption):
    name = 'magic_quotes_sybase'
    verbose_name=_("Magic quotes sybase")
    help_text=_("Single-quote is escaped with a single-quote instead of a backslash (On or Off).")
    regex=r'^(On|Off|on|off)$'
    group = AppOption.PHP


class PHPMaxExecutonTime(AppOption):
    name = 'max_execution_time'
    verbose_name=_("Max execution time")
    help_text=_("Maximum time in seconds a script is allowed to run before it is terminated by "
                "the parser (Integer between 0 and 999).")
    regex=r'^[0-9]{1,3}$'
    group = AppOption.PHP


class PHPMaxInputTime(AppOption):
    name = 'max_input_time'
    verbose_name=_("Max input time")
    help_text=_("Maximum time in seconds a script is allowed to parse input data, like POST and GET "
                "(Integer between 0 and 999).")
    regex=r'^[0-9]{1,3}$'
    group = AppOption.PHP


class PHPMaxInputVars(AppOption):
    name = 'max_input_vars'
    verbose_name=_("Max input vars")
    help_text=_("How many input variables may be accepted (limit is applied to $_GET, $_POST "
                "and $_COOKIE superglobal separately) (Integer between 0 and 9999).")
    regex=r'^[0-9]{1,4}$'
    group = AppOption.PHP


class PHPMemoryLimit(AppOption):
    name = 'memory_limit'
    verbose_name=_("Memory limit")
    help_text=_("This sets the maximum amount of memory in bytes that a script is allowed to allocate "
                "(Value between 0M and 999M).")
    regex=r'^[0-9]{1,3}M$'
    group = AppOption.PHP


class PHPMySQLConnectTimeout(AppOption):
    name = 'mysql.connect_timeout'
    verbose_name=_("Mysql connect timeout")
    help_text=_("Number between 0 and 999.")
    regex=r'^([0-9]){1,3}$'
    group = AppOption.PHP


class PHPOutputBuffering(AppOption):
    name = 'output_buffering'
    verbose_name=_("Output buffering")
    help_text=_("Turn on output buffering (On or Off).")
    regex=r'^(On|Off|on|off)$'
    group = AppOption.PHP


class PHPRegisterGlobals(AppOption):
    name = 'register_globals'
    verbose_name=_("Register globals")
    help_text=_("Whether or not to register the EGPCS (Environment, GET, POST, Cookie, Server) "
                "variables as global variables (On or Off).")
    regex=r'^(On|Off|on|off)$'
    group = AppOption.PHP


class PHPPostMaxSize(AppOption):
    name = 'post_max_size'
    verbose_name=_("Post max size")
    help_text=_("Sets max size of post data allowed (Value between 0M and 999M).")
    regex=r'^[0-9]{1,3}M$'
    group = AppOption.PHP


class PHPSendmailPath(AppOption):
    name = 'sendmail_path'
    verbose_name=_("sendmail_path")
    help_text=_("Where the sendmail program can be found.")
    regex=r'^[^ ]+$'
    group = AppOption.PHP


class PHPSessionBugCompatWarn(AppOption):
    name = 'session.bug_compat_warn'
    verbose_name=_("session.bug_compat_warn")
    help_text=_("Enables an PHP bug on session initialization for legacy behaviour (On or Off).")
    regex=r'^(On|Off|on|off)$'
    group = AppOption.PHP


class PHPSessionAutoStart(AppOption):
    name = 'session.auto_start',
    verbose_name=_("session.auto_start")
    help_text=_("Specifies whether the session module starts a session automatically on request "
                "startup (On or Off).")
    regex=r'^(On|Off|on|off)$'
    group = AppOption.PHP


class PHPSafeMode(AppOption):
    name = 'safe_mode'
    verbose_name=_("Safe mode")
    help_text=_("Whether to enable PHP's safe mode (On or Off) <b>DEPRECATED as of PHP 5.3.0</b>")
    regex=r'^(On|Off|on|off)$'
    deprecated=5.3
    group = AppOption.PHP


class PHPSuhosinPostMaxVars(AppOption):
    name = 'suhosin.post.max_vars',
    verbose_name=_("Suhosin POST max vars")
    help_text=_("Number between 0 and 9999.")
    regex=r'^[0-9]{1,4}$'
    group = AppOption.PHP


class PHPSuhosinGetMaxVars(AppOption):
    name = 'suhosin.get.max_vars'
    verbose_name=_("Suhosin GET max vars")
    help_text=_("Number between 0 and 9999.")
    regex=r'^[0-9]{1,4}$'
    group = AppOption.PHP


class PHPSuhosinRequestMaxVars(AppOption):
    name = 'suhosin.request.max_vars'
    verbose_name=_("Suhosin request max vars")
    help_text=_("Number between 0 and 9999.")
    regex=r'^[0-9]{1,4}$'
    group = AppOption.PHP


class PHPSuhosinSessionEncrypt(AppOption):
    name = 'suhosin.session.encrypt'
    verbose_name=_("suhosin.session.encrypt")
    help_text=_("On or Off")
    regex=r'^(On|Off|on|off)$'
    group = AppOption.PHP


class PHPSuhosinSimulation(AppOption):
    name = 'suhosin.simulation'
    verbose_name=_("Suhosin simulation")
    help_text=_("On or Off")
    regex=r'^(On|Off|on|off)$'
    group = AppOption.PHP


class PHPSuhosinExecutorIncludeWhitelist(AppOption):
    name = 'suhosin.executor.include.whitelist'
    verbose_name=_("suhosin.executor.include.whitelist")
    regex=r'.*$'
    group = AppOption.PHP


class PHPUploadMaxFileSize(AppOption):
    name = 'upload_max_filesize',
    verbose_name=_("upload_max_filesize")
    help_text=_("Value between 0M and 999M.")
    regex=r'^[0-9]{1,3}M$'
    group = AppOption.PHP


class PHPPostMaxSize(AppOption):
    name = 'post_max_size'
    verbose_name=_("zend_extension")
    regex=r'^[^ ]+$'
    group = AppOption.PHP
