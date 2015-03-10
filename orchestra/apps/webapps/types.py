import os

from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra import plugins
from orchestra.plugins.forms import PluginDataForm
from orchestra.core import validators
from orchestra.forms import widgets
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from . import options, settings
from .options import AppOption


class AppType(plugins.Plugin):
    name = None
    verbose_name = ""
    help_text= ""
    form = PluginDataForm
    change_form = None
    serializer = None
    icon = 'orchestra/icons/apps.png'
    unique_name = False
    option_groups = (AppOption.FILESYSTEM, AppOption.PROCESS, AppOption.PHP)
    
    @classmethod
    @cached
    def get_plugins(cls):
        plugins = []
        for cls in settings.WEBAPPS_TYPES:
            plugins.append(import_class(cls))
        return plugins
    
    def clean_data(self, webapp):
        """ model clean, uses cls.serizlier by default """
        if self.serializer:
            serializer = self.serializer(data=webapp.data)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)
            return serializer.data
        return {}
    
    def get_directive(self, webapp):
        return ('static', webapp.get_path())
    
    def get_form(self):
        self.form.plugin = self
        self.form.plugin_field = 'type'
        return self.form
    
    def get_change_form(self):
        form = self.change_form or self.form
        form.plugin = self
        form.plugin_field = 'type'
        return form
    
    def get_serializer(self):
        self.serializer.plugin = self
        return self.serializer
    
    def validate(self, instance):
        """ Unique name validation """
        if self.unique_name:
            if not instance.pk and Webapp.objects.filter(name=instance.name, type=instance.type).exists():
                raise ValidationError({
                    'name': _("A WordPress blog with this name already exists."),
                })
    
    @classmethod
    @cached
    def get_php_options(cls):
        php_version = getattr(cls, 'php_version', 1)
        php_options = AppOption.get_option_groups()[AppOption.PHP]
        return [op for op in php_options if getattr(cls, 'deprecated', 99) > php_version]
    
    @classmethod
    @cached
    def get_options(cls):
        """ Get enabled options based on cls.option_groups """
        groups = AppOption.get_option_groups()
        options = []
        for group in cls.option_groups:
            group_options = groups[group]
            if group == AppOption.PHP:
                group_options = cls.get_php_options()
            if group is None:
                options.insert(0, (group, group_options))
            else:
                options.append((group, group_options))
        return options
    
    @classmethod
    def get_options_choices(cls):
        """ Generates grouped choices ready to use in Field.choices """
        # generators can not be @cached
        yield (None, '-------')
        for group, options in cls.get_options():
            if group is None:
                for option in options:
                    yield (option.name, option.verbose_name)
            else:
                yield (group, [(op.name, op.verbose_name) for op in options])
    
    def save(self, instance):
        pass
    
    def delete(self, instance):
        pass
    
    def get_related_objects(self, instance):
        pass
    
    def get_directive_context(self, webapp):
        return {
            'app_id': webapp.id,
            'app_name': webapp.name,
            'user': webapp.account.username,
        }


class PHPAppType(AppType):
    php_version = 5.4
    fpm_listen = settings.WEBAPPS_FPM_LISTEN
    
    def get_directive(self, webapp):
        context = self.get_directive_context(webapp)
        socket_type = 'unix'
        if ':' in self.fpm_listen:
            socket_type = 'tcp'
        socket = self.fpm_listen % context
        return ('fpm', socket_type, socket, webapp.get_path())
    
    def get_context(self, webapp):
        """ context used to format settings """
        return {
            'home': webapp.account.main_systemuser.get_home(),
            'account': webapp.account.username,
            'user': webapp.account.username,
            'app_name': webapp.name,
        }
    
    def get_php_init_vars(self, webapp, per_account=False):
        """
        process php options for inclusion on php.ini
        per_account=True merges all (account, webapp.type) options
        """
        init_vars = {}
        options = webapp.options.all()
        if per_account:
            options = webapp.account.webapps.filter(webapp_type=webapp.type)
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
            context = self.get_context(webapp)
            error_log_path = os.path.normpath(settings.WEBAPPS_PHP_ERROR_LOG_PATH % context)
            init_vars['error_log'] = error_log_path
        return init_vars


class PHP54App(PHPAppType):
    name = 'php5.4-fpm'
    php_version = 5.4
    verbose_name = "PHP 5.4 FPM"
    help_text = _("This creates a PHP5.5 application under ~/webapps/&lt;app_name&gt;<br>"
                  "PHP-FPM will be used to execute PHP files.")
    icon = 'orchestra/icons/apps/PHPFPM.png'


class PHP53App(PHPAppType):
    name = 'php5.3-fcgid'
    php_version = 5.3
    php_binary = '/usr/bin/php5-cgi'
    php_rc = '/etc/php5/cgi/'
    verbose_name = "PHP 5.3 FCGID"
    help_text = _("This creates a PHP5.3 application under ~/webapps/&lt;app_name&gt;<br>"
                  "Apache-mod-fcgid will be used to execute PHP files.")
    icon = 'orchestra/icons/apps/PHPFCGI.png'
    
    def get_directive(self, webapp):
        context = self.get_directive_context(webapp)
        wrapper_path = os.path.normpath(settings.WEBAPPS_FCGID_PATH % context)
        return ('fcgid', webapp.get_path(), wrapper_path)


class PHP52App(PHP53App):
    name = 'php5.2-fcgid'
    php_version = 5.2
    php_binary = '/usr/bin/php5.2-cgi'
    php_rc = '/etc/php5.2/cgi/'
    verbose_name = "PHP 5.2 FCGID"
    help_text = _("This creates a PHP5.2 application under ~/webapps/&lt;app_name&gt;<br>"
                  "Apache-mod-fcgid will be used to execute PHP files.")
    icon = 'orchestra/icons/apps/PHPFCGI.png'


class PHP4App(PHP53App):
    name = 'php4-fcgid'
    php_version = 4
    php_binary = '/usr/bin/php4-cgi'
    verbose_name = "PHP 4 FCGID"
    help_text = _("This creates a PHP4 application under ~/webapps/&lt;app_name&gt;<br>"
                  "Apache-mod-fcgid will be used to execute PHP files.")
    icon = 'orchestra/icons/apps/PHPFCGI.png'


class StaticApp(AppType):
    name = 'static'
    verbose_name = "Static"
    help_text = _("This creates a Static application under ~/webapps/&lt;app_name&gt;<br>"
                  "Apache2 will be used to serve static content and execute CGI files.")
    icon = 'orchestra/icons/apps/Static.png'
    option_groups = (AppOption.FILESYSTEM,)


class WebalizerApp(AppType):
    name = 'webalizer'
    verbose_name = "Webalizer"
    directive = ('static', '%(app_path)s%(site_name)s')
    help_text = _("This creates a Webalizer application under "
                  "~/webapps/&lt;app_name&gt;-&lt;site_name&gt;")
    icon = 'orchestra/icons/apps/Stats.png'
    option_groups = ()
    
    def get_directive(self, webapp):
        webalizer_path = os.path.join(webapp.get_path(), '%(site_name)s')
        webalizer_path = os.path.normpath(webalizer_path)
        return ('static', webalizer_path)


class WordPressMuApp(PHPAppType):
    name = 'wordpress-mu'
    verbose_name = "WordPress (SaaS)"
    directive = ('fpm', 'fcgi://127.0.0.1:8990/home/httpd/wordpress-mu/')
    help_text = _("This creates a WordPress site on a multi-tenant WordPress server.<br>"
                  "By default this blog is accessible via &lt;app_name&gt;.blogs.orchestra.lan")
    icon = 'orchestra/icons/apps/WordPressMu.png'
    unique_name = True
    option_groups = ()
    fpm_listen = settings.WEBAPPS_WORDPRESSMU_LISTEN


class DokuWikiMuApp(PHPAppType):
    name = 'dokuwiki-mu'
    verbose_name = "DokuWiki (SaaS)"
    directive = ('alias', '/home/httpd/wikifarm/farm/')
    help_text = _("This create a DokuWiki wiki into a shared DokuWiki server.<br>"
                  "By default this wiki is accessible via &lt;app_name&gt;.wikis.orchestra.lan")
    icon = 'orchestra/icons/apps/DokuWikiMu.png'
    unique_name = True
    option_groups = ()
    fpm_listen = settings.WEBAPPS_DOKUWIKIMU_LISTEN


class MoodleMuApp(PHPAppType):
    name = 'moodle-mu'
    verbose_name = "Moodle (SaaS)"
    directive = ('alias', '/home/httpd/wikifarm/farm/')
    help_text = _("This create a Moodle site into a shared Moodle server.<br>"
                  "By default this wiki is accessible via &lt;app_name&gt;.moodle.orchestra.lan")
    icon = 'orchestra/icons/apps/MoodleMu.png'
    unique_name = True
    option_groups = ()
    fpm_listen = settings.WEBAPPS_MOODLEMU_LISTEN


class DrupalMuApp(PHPAppType):
    name = 'drupal-mu'
    verbose_name = "Drupdal (SaaS)"
    directive = ('fpm', 'fcgi://127.0.0.1:8991/home/httpd/drupal-mu/')
    help_text = _("This creates a Drupal site into a multi-tenant Drupal server.<br>"
                  "The installation will be completed after visiting "
                  "http://&lt;app_name&gt;.drupal.orchestra.lan/install.php?profile=standard<br>"
                  "By default this site will be accessible via &lt;app_name&gt;.drupal.orchestra.lan")
    icon = 'orchestra/icons/apps/DrupalMu.png'
    unique_name = True
    option_groups = ()
    fpm_listen = settings.WEBAPPS_DRUPALMU_LISTEN


from rest_framework import serializers
from orchestra.forms import widgets
class SymbolicLinkForm(PluginDataForm):
    path = forms.CharField(label=_("Path"), widget=forms.TextInput(attrs={'size':'100'}),
            help_text=_("Path for the origin of the symbolic link."))


class SymbolicLinkSerializer(serializers.Serializer):
    path = serializers.CharField(label=_("Path"))


class SymbolicLinkApp(PHPAppType):
    name = 'symbolic-link'
    verbose_name = "Symbolic link"
    form = SymbolicLinkForm
    serializer = SymbolicLinkSerializer
    icon = 'orchestra/icons/apps/SymbolicLink.png'
    change_readonly_fileds = ('path',)


class WordPressForm(PluginDataForm):
    db_name = forms.CharField(label=_("Database name"),
            help_text=_("Database used for this webapp."))
    db_user = forms.CharField(label=_("Database user"),)
    db_pass = forms.CharField(label=_("Database user password"),
            help_text=_("Initial database password."))


class WordPressSerializer(serializers.Serializer):
    db_name = serializers.CharField(label=_("Database name"), required=False)
    db_user = serializers.CharField(label=_("Database user"), required=False)
    db_pass = serializers.CharField(label=_("Database user password"), required=False)


from orchestra.apps.databases.models import Database, DatabaseUser
from orchestra.utils.python import random_ascii


class WordPressApp(PHPAppType):
    name = 'wordpress'
    verbose_name = "WordPress"
    icon = 'orchestra/icons/apps/WordPress.png'
    change_form = WordPressForm
    serializer = WordPressSerializer
    change_readonly_fileds = ('db_name', 'db_user', 'db_pass',)
    help_text = _("Visit http://&lt;domain.lan&gt;/wp-admin/install.php to finish the installation.")
    
    def get_db_name(self, webapp):
        db_name = 'wp_%s_%s' % (webapp.name, webapp.account)
        # Limit for mysql database names
        return db_name[:65]
    
    def get_db_user(self, webapp):
        db_name = self.get_db_name(webapp)
        # Limit for mysql user names
        return db_name[:17]
    
    def get_db_pass(self):
        return random_ascii(10)
    
    def validate(self, webapp):
        create = not webapp.pk
        if create:
            db = Database(name=self.get_db_name(webapp), account=webapp.account)
            user = DatabaseUser(username=self.get_db_user(webapp), password=self.get_db_pass(),
                    account=webapp.account)
            for obj in (db, user):
                try:
                    obj.full_clean()
                except ValidationError, e:
                    raise ValidationError({
                        'name': e.messages,
                    })
    
    def save(self, webapp):
        create = not webapp.pk
        if create:
            db_name = self.get_db_name(webapp)
            db_user = self.get_db_user(webapp)
            db_pass = self.get_db_pass()
            db = Database.objects.create(name=db_name, account=webapp.account)
            user = DatabaseUser(username=db_user, account=webapp.account)
            user.set_password(db_pass)
            user.save()
            db.users.add(user)
            webapp.data = {
                'db_name': db_name,
                'db_user': db_user,
                'db_pass': db_pass,
            }
        else:
            # Trigger related backends
            for related in self.get_related(webapp):
                related.save()
        
    def delete(self, webapp):
        for related in self.get_related(webapp):
            related.delete()
    
    def get_related(self, webapp):
        related = []
        try:
            db_user = DatabaseUser.objects.get(username=webapp.data.get('db_user'))
        except DatabaseUser.DoesNotExist:
            pass
        else:
            related.append(db_user)
        try:
            db = Database.objects.get(name=webapp.data.get('db_name'))
        except Database.DoesNotExist:
            pass
        else:
            related.append(db)
        return related
