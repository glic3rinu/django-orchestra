import os
import re
from collections import OrderedDict

from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.plugins.forms import PluginDataForm
from orchestra.utils.functional import cached

from .. import settings
from ..options import AppOption

from . import AppType


help_message = _("Version of PHP used to execute this webapp. <br>"
    "Changing the PHP version may result in application malfunction, "
    "make sure that everything continue to work as expected.")


class PHPAppForm(PluginDataForm):
    php_version = forms.ChoiceField(label=_("PHP version"),
            choices=settings.WEBAPPS_PHP_VERSIONS,
            initial=settings.WEBAPPS_DEFAULT_PHP_VERSION,
            help_text=help_message)


class PHPAppSerializer(serializers.Serializer):
    php_version = serializers.ChoiceField(label=_("PHP version"),
            choices=settings.WEBAPPS_PHP_VERSIONS,
            default=settings.WEBAPPS_DEFAULT_PHP_VERSION,
            help_text=help_message)


class PHPApp(AppType):
    name = 'php'
    verbose_name = "PHP"
    help_text = _("This creates a PHP application under ~/webapps/&lt;app_name&gt;<br>")
    form = PHPAppForm
    serializer = PHPAppSerializer
    icon = 'orchestra/icons/apps/PHP.png'
    
    DEFAULT_PHP_VERSION = settings.WEBAPPS_DEFAULT_PHP_VERSION
    PHP_DISABLED_FUNCTIONS = settings.WEBAPPS_PHP_DISABLED_FUNCTIONS
    PHP_ERROR_LOG_PATH = settings.WEBAPPS_PHP_ERROR_LOG_PATH
    FPM_LISTEN = settings.WEBAPPS_FPM_LISTEN
    FCGID_WRAPPER_PATH = settings.WEBAPPS_FCGID_WRAPPER_PATH
    
    @property
    def is_fpm(self):
        return self.get_php_version().endswith('-fpm')
    
    @property
    def is_fcgid(self):
        return self.get_php_version().endswith('-cgi')
    
    def get_detail(self):
        return self.instance.data.get('php_version', '')
    
    @cached
    def get_php_options(self):
        php_version = float(self.get_php_version_number())
        php_options = AppOption.get_option_groups()[AppOption.PHP]
        return [op for op in php_options if (op.deprecated or 999) > php_version]
    
    def get_php_init_vars(self, merge=False):
        """
        process php options for inclusion on php.ini
        per_account=True merges all (account, webapp.type) options
        """
        init_vars = OrderedDict()
        options = self.instance.options.all().order_by('name')
        if merge:
            # Get options from the same account and php_version webapps
            options = []
            php_version = self.get_php_version()
            webapps = self.instance.account.webapps.filter(type=self.instance.type)
            for webapp in webapps:
                if webapp.type_instance.get_php_version() == php_version:
                    options += list(webapp.options.all())
        php_options = [option.name for option in self.get_php_options()]
        enabled_functions = set()
        for opt in options:
            if opt.name in php_options:
                if opt.name == 'enable_functions':
                    enabled_functions = enabled_functions.union(set(opt.value.split(',')))
                else:
                    init_vars[opt.name] = opt.value
        if enabled_functions:
            disabled_functions = []
            for function in self.PHP_DISABLED_FUNCTIONS:
                if function not in enabled_functions:
                    disabled_functions.append(function)
            init_vars['disable_functions'] = ','.join(disabled_functions)
        timeout = self.instance.options.filter(name='timeout').first()
        if timeout:
            # Give a little slack here
            timeout = str(int(timeout.value)-2)
            init_vars['max_execution_time'] = timeout
        if self.PHP_ERROR_LOG_PATH and 'error_log' not in init_vars:
            context = self.get_directive_context()
            error_log_path = os.path.normpath(self.PHP_ERROR_LOG_PATH % context)
            init_vars['error_log'] = error_log_path
        return init_vars
    
    def get_directive_context(self):
        context = super(PHPApp, self).get_directive_context()
        context.update({
            'php_version': self.get_php_version(),
            'php_version_number': self.get_php_version_number(),
        })
        return context
    
    def get_directive(self):
        context = self.get_directive_context()
        if self.is_fpm:
            socket = self.FPM_LISTEN % context
            return ('fpm', socket, self.instance.get_path())
        elif self.is_fcgid:
            wrapper_path = os.path.normpath(self.FCGID_WRAPPER_PATH % context)
            return ('fcgid', self.instance.get_path(), wrapper_path)
        else:
            php_version = self.get_php_version()
            raise ValueError("Unknown directive for php version '%s'" % php_version)
    
    def get_php_version(self):
        default_version = self.DEFAULT_PHP_VERSION
        return self.instance.data.get('php_version', default_version)
    
    def get_php_version_number(self):
        php_version = self.get_php_version()
        number = re.findall(r'[0-9]+\.?[0-9]?', php_version)
        if not number:
            raise ValueError("No version number matches for '%s'" % php_version)
        if len(number) > 1:
            raise ValueError("Multiple version number matches for '%s'" % php_version)
        return number[0]
