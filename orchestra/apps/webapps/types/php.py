import os

from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.forms import widgets
from orchestra.plugins.forms import PluginDataForm

from .. import settings

from . import AppType


class PHPAppType(AppType):
    FPM = 'fpm'
    FCGID = 'fcgid'
    
    php_version = 5.4
    fpm_listen = settings.WEBAPPS_FPM_LISTEN
    
    def get_context(self):
        """ context used to format settings """
        return {
            'home': self.instance.account.main_systemuser.get_home(),
            'account': self.instance.account.username,
            'user': self.instance.account.username,
            'app_name': self.instance.name,
        }
    
    def get_php_init_vars(self, per_account=False):
        """
        process php options for inclusion on php.ini
        per_account=True merges all (account, webapp.type) options
        """
        init_vars = {}
        options = self.instance.options.all()
        if per_account:
            options = self.instance.account.webapps.filter(webapp_type=self.instance.type)
        php_options = [option.name for option in type(self).get_php_options()]
        for opt in options:
            if opt.name in php_options:
                init_vars[opt.name] = opt.value
        enabled_functions = []
        for value in options.filter(name='enabled_functions').values_list('value', flat=True):
            enabled_functions += enabled_functions.get().value.split(',')
        if enabled_functions:
            disabled_functions = []
            for function in settings.WEBAPPS_PHP_DISABLED_FUNCTIONS:
                if function not in enabled_functions:
                    disabled_functions.append(function)
            init_vars['dissabled_functions'] = ','.join(disabled_functions)
        if settings.WEBAPPS_PHP_ERROR_LOG_PATH and 'error_log' not in init_vars:
            context = self.get_context()
            error_log_path = os.path.normpath(settings.WEBAPPS_PHP_ERROR_LOG_PATH % context)
            init_vars['error_log'] = error_log_path
        return init_vars


help_message = _("Version of PHP used to execute this webapp. <br>"
    "Changing the PHP version may result in application malfunction, "
    "make sure that everything continue to work as expected.")


class PHPFPMAppForm(PluginDataForm):
    php_version = forms.ChoiceField(label=_("PHP version"),
            choices=settings.WEBAPPS_PHP_FPM_VERSIONS,
            initial=settings.WEBAPPS_PHP_FPM_DEFAULT_VERSION,
            help_text=help_message)


class PHPFPMAppSerializer(serializers.Serializer):
    php_version = serializers.ChoiceField(label=_("PHP version"),
            choices=settings.WEBAPPS_PHP_FPM_VERSIONS,
            default=settings.WEBAPPS_PHP_FPM_DEFAULT_VERSION,
            help_text=help_message)


class PHPFPMApp(PHPAppType):
    name = 'php-fpm'
    php_execution = PHPAppType.FPM
    verbose_name = "PHP FPM"
    help_text = _("This creates a PHP application under ~/webapps/&lt;app_name&gt;<br>"
                  "PHP-FPM will be used to execute PHP files.")
    icon = 'orchestra/icons/apps/PHPFPM.png'
    form = PHPFPMAppForm
    serializer = PHPFPMAppSerializer
    
    def get_directive(self):
        context = self.get_directive_context()
        socket_type = 'unix'
        if ':' in self.fpm_listen:
            socket_type = 'tcp'
        socket = self.fpm_listen % context
        return ('fpm', socket_type, socket, self.instance.get_path())


class PHPFCGIDAppForm(PluginDataForm):
    php_version = forms.ChoiceField(label=_("PHP version"),
            choices=settings.WEBAPPS_PHP_FCGID_VERSIONS,
            initial=settings.WEBAPPS_PHP_FCGID_DEFAULT_VERSION,
            help_text=help_message)


class PHPFCGIDAppSerializer(serializers.Serializer):
    php_version = serializers.ChoiceField(label=_("PHP version"),
            choices=settings.WEBAPPS_PHP_FCGID_VERSIONS,
            default=settings.WEBAPPS_PHP_FCGID_DEFAULT_VERSION,
            help_text=help_message)


class PHPFCGIDApp(PHPAppType):
    name = 'php-fcgid'
    php_execution = PHPAppType.FCGID
    verbose_name = "PHP FCGID"
    help_text = _("This creates a PHP application under ~/webapps/&lt;app_name&gt;<br>"
                  "Apache-mod-fcgid will be used to execute PHP files.")
    icon = 'orchestra/icons/apps/PHPFCGI.png'
    form = PHPFCGIDAppForm
    serializer = PHPFCGIDAppSerializer
    
    def get_directive(self):
        context = self.get_directive_context()
        wrapper_path = os.path.normpath(settings.WEBAPPS_FCGID_PATH % context)
        return ('fcgid', self.instance.get_path(), wrapper_path)
    
    def get_php_binary_path(self):
        default_version = settings.WEBAPPS_PHP_FCGID_DEFAULT_VERSION
        context = {
            'php_version': self.instance.data.get('php_version', default_version)
        }
        return os.path.normpath(settings.WEBAPPS_PHP_CGI_BINARY_PATH % context)
    
    def get_php_rc_path(self):
        default_version = settings.WEBAPPS_PHP_FCGID_DEFAULT_VERSION
        context = {
            'php_version': self.instance.data.get('php_version', default_version)
        }
        return os.path.normpath(settings.WEBAPPS_PHP_CGI_RC_PATH % context)

