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


class AppType(plugins.Plugin):
    name = None
    verbose_name = ""
    help_text= ""
    form = PluginDataForm
    change_form = None
    serializer = None
    icon = 'orchestra/icons/apps.png'
    unique_name = False
    options = (
        ('Process', options.process),
        ('PHP', options.php),
        ('File system', options.filesystem),
    )
    
    @classmethod
    @cached
    def get_plugins(cls):
        plugins = []
        for cls in settings.WEBAPPS_TYPES:
            plugins.append(import_class(cls))
        return plugins
    
    @classmethod
    def clean_data(cls, webapp):
        """ model clean, uses cls.serizlier by default """
        if cls.serializer:
            serializer = cls.serializer(data=webapp.data)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)
            return serializer.data
        return {}
    
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
    
    def get_options(self):
        pass
    
    @classmethod
    def get_options_choices(cls):
        enabled = options.get_enabled().values()
        yield (None, '-------')
        for option in cls.options:
            if hasattr(option, '__iter__'):
                yield (option[0], [(op.name, op.verbose_name) for op in option[1] if op in enabled])
            elif option in enabled:
                yield (option.name, option.verbose_name)
    
    
    def save(self, instance):
        pass
    
    def delete(self, instance):
        pass
    
    def get_related_objects(self, instance):
        pass


class Php55App(AppType):
    name = 'php5.5-fpm'
    verbose_name = "PHP 5.5 FPM"
#        'fpm', ('unix:/var/run/%(user)s-%(app_name)s.sock|fcgi://127.0.0.1%(app_path)s',),
    directive = ('fpm', 'fcgi://{}%(app_path)s'.format(settings.WEBAPPS_FPM_LISTEN))
    help_text = _("This creates a PHP5.5 application under ~/webapps/&lt;app_name&gt;<br>"
                  "PHP-FPM will be used to execute PHP files.")
    options = (
        ('Process', options.process),
        ('PHP', [op for op in options.php if getattr(op, 'deprecated', 99) > 5.5]),
        ('File system', options.filesystem),
    )
    icon = 'orchestra/icons/apps/PHPFPM.png'


class Php52App(AppType):
    name = 'php5.2-fcgi'
    verbose_name = "PHP 5.2 FCGI"
    directive = ('fcgi', settings.WEBAPPS_FCGID_PATH)
    help_text = _("This creates a PHP5.2 application under ~/webapps/&lt;app_name&gt;<br>"
                  "Apache-mod-fcgid will be used to execute PHP files.")
    icon = 'orchestra/icons/apps/PHPFCGI.png'


class Php4App(AppType):
    name = 'php4-fcgi'
    verbose_name = "PHP 4 FCGI"
    directive = ('fcgi', settings.WEBAPPS_FCGID_PATH)
    help_text = _("This creates a PHP4 application under ~/webapps/&lt;app_name&gt;<br>"
                  "Apache-mod-fcgid will be used to execute PHP files.")
    icon = 'orchestra/icons/apps/PHPFCGI.png'


class StaticApp(AppType):
    name = 'static'
    verbose_name = "Static"
    directive = ('static',)
    help_text = _("This creates a Static application under ~/webapps/&lt;app_name&gt;<br>"
                  "Apache2 will be used to serve static content and execute CGI files.")
    icon = 'orchestra/icons/apps/Static.png'
    options = (
        ('File system', options.filesystem),
    )

class WebalizerApp(AppType):
    name = 'webalizer'
    verbose_name = "Webalizer"
    directive = ('static', '%(app_path)s%(site_name)s')
    help_text = _("This creates a Webalizer application under "
                  "~/webapps/&lt;app_name&gt;-&lt;site_name&gt;")
    icon = 'orchestra/icons/apps/Stats.png'
    options = ()


class WordPressMuApp(AppType):
    name = 'wordpress-mu'
    verbose_name = "WordPress (SaaS)"
    directive = ('fpm', 'fcgi://127.0.0.1:8990/home/httpd/wordpress-mu/')
    help_text = _("This creates a WordPress site on a multi-tenant WordPress server.<br>"
                  "By default this blog is accessible via &lt;app_name&gt;.blogs.orchestra.lan")
    icon = 'orchestra/icons/apps/WordPressMu.png'
    unique_name = True
    options = ()


class DokuWikiMuApp(AppType):
    name = 'dokuwiki-mu'
    verbose_name = "DokuWiki (SaaS)"
    directive = ('alias', '/home/httpd/wikifarm/farm/')
    help_text = _("This create a DokuWiki wiki into a shared DokuWiki server.<br>"
                  "By default this wiki is accessible via &lt;app_name&gt;.wikis.orchestra.lan")
    icon = 'orchestra/icons/apps/DokuWikiMu.png'
    unique_name = True
    options = ()


class MoodleMuApp(AppType):
    name = 'moodle-mu'
    verbose_name = "Moodle (SaaS)"
    directive = ('alias', '/home/httpd/wikifarm/farm/')
    help_text = _("This create a Moodle site into a shared Moodle server.<br>"
                  "By default this wiki is accessible via &lt;app_name&gt;.moodle.orchestra.lan")
    icon = 'orchestra/icons/apps/MoodleMu.png'
    unique_name = True
    options = ()


class DrupalMuApp(AppType):
    name = 'drupal-mu'
    verbose_name = "Drupdal (SaaS)"
    directive = ('fpm', 'fcgi://127.0.0.1:8991/home/httpd/drupal-mu/')
    help_text = _("This creates a Drupal site into a multi-tenant Drupal server.<br>"
                  "The installation will be completed after visiting "
                  "http://&lt;app_name&gt;.drupal.orchestra.lan/install.php?profile=standard<br>"
                  "By default this site will be accessible via &lt;app_name&gt;.drupal.orchestra.lan")
    icon = 'orchestra/icons/apps/DrupalMu.png'
    unique_name = True
    options = ()


from rest_framework import serializers
from orchestra.forms import widgets
class SymbolicLinkForm(PluginDataForm):
    path = forms.CharField(label=_("Path"), widget=forms.TextInput(attrs={'size':'100'}),
            help_text=_("Path for the origin of the symbolic link."))


class SymbolicLinkSerializer(serializers.Serializer):
    path = serializers.CharField(label=_("Path"))


class SymbolicLinkApp(AppType):
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


class WordPressApp(AppType):
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
