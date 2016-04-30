import importlib
import os
from functools import lru_cache
from urllib.parse import urlparse

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from orchestra import plugins
from orchestra.contrib.databases.models import Database, DatabaseUser
from orchestra.contrib.orchestration import Operation
from orchestra.contrib.websites.models import Website, WebsiteDirective
from orchestra.utils.apps import isinstalled
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from . import helpers
from .. import settings
from ..forms import SaaSPasswordForm


class SoftwareService(plugins.Plugin, metaclass=plugins.PluginMount):
    PROTOCOL_MAP = {
        'http': (Website.HTTP, (Website.HTTP, Website.HTTP_AND_HTTPS)),
        'https': (Website.HTTPS_ONLY, (Website.HTTPS, Website.HTTP_AND_HTTPS, Website.HTTPS_ONLY)),
    }
    
    name = None
    verbose_name = None
    form = SaaSPasswordForm
    site_domain = None
    has_custom_domain = False
    icon = 'orchestra/icons/apps.png'
    class_verbose_name = _("Software as a Service")
    plugin_field = 'service'
    allow_custom_url = False
    
    @classmethod
    @lru_cache()
    def get_plugins(cls, all=False):
        if all:
            for module in os.listdir(os.path.dirname(__file__)):
                if module not in ('options.py', '__init__.py') and module[-3:] == '.py':
                    importlib.import_module('.'+module[:-3], __package__)
            plugins = super().get_plugins()
        else:
            plugins = []
            for cls in settings.SAAS_ENABLED_SERVICES:
                plugins.append(import_class(cls))
        return plugins
    
    def get_change_readonly_fields(cls):
        fields = super(SoftwareService, cls).get_change_readonly_fields()
        return fields + ('name',)
    
    def get_site_domain(self):
        context = {
            'site_name': self.instance.name,
            'name': self.instance.name,
        }
        return self.site_domain % context
    
    def clean(self):
        if self.allow_custom_url:
            if self.instance.custom_url:
                if isinstalled('orchestra.contrib.websites'):
                    helpers.clean_custom_url(self)
        elif self.instance.custom_url:
            raise ValidationError({
                'custom_url': _("Custom URL not allowed for this service."),
            })
    
    def clean_data(self):
        data = super(SoftwareService, self).clean_data()
        if not self.instance.pk:
            try:
                log = Operation.execute_action(self.instance, 'validate_creation')[0]
            except IndexError:
                pass
            else:
                if log.state != log.SUCCESS:
                    raise ValidationError(_("Validate creation execution has failed."))
                errors = {}
                if 'user-exists' in log.stdout:
                    errors['name'] = _("User with this username already exists.")
                if 'email-exists' in log.stdout:
                    errors['email'] = _("User with this email address already exists.")
                if errors:
                    raise ValidationError(errors)
        return data
    
    def get_directive_name(self):
        return '%s-saas' % self.name
    
    def get_directive(self, *args):
        if not args:
            instance = self.instance
        else:
            instance = args[0]
        url = urlparse(instance.custom_url)
        account = instance.account
        return WebsiteDirective.objects.get(
            name=self.get_directive_name(),
            value=url.path,
            website__protocol__in=self.PROTOCOL_MAP[url.scheme][1],
            website__domains__name=url.netloc,
            website__account=account,
        )
    
    def get_website(self):
        url = urlparse(self.instance.custom_url)
        account = self.instance.account
        return Website.objects.get(
            protocol__in=self.PROTOCOL_MAP[url.scheme][1],
            domains__name=url.netloc,
            account=account,
            directives__name=self.get_directive_name(),
            directives__value=url.path,
        )
    
    def create_or_update_directive(self):
        return helpers.create_or_update_directive(self)
    
    def delete_directive(self):
        directive = None
        try:
            old = type(self.instance).objects.get(pk=self.instance.pk)
            if old.custom_url:
                directive = self.get_directive(old)
        except ObjectDoesNotExist:
            return
        if directive is not None:
            directive.delete()
    
    def save(self):
        # pre instance.save()
        if isinstalled('orchestra.contrib.websites'):
            if self.instance.custom_url:
                self.create_or_update_directive()
            elif self.instance.pk:
                self.delete_directive()
    
    def delete(self):
        if isinstalled('orchestra.contrib.websites'):
            self.delete_directive()
    
    def get_related(self):
        return []


class DBSoftwareService(SoftwareService):
    db_name = None
    db_user = None
    abstract = True
    
    def get_db_name(self):
        context = {
            'name': self.instance.name,
            'site_name': self.instance.name,
        }
        db_name = self.db_name % context
        # Limit for mysql database names
        return db_name[:65]
    
    def get_db_user(self):
        return self.db_user
    
    @cached
    def get_account(self):
        account_model = self.instance._meta.get_field('account')
        return account_model.rel.to.objects.get_main()
    
    def validate(self):
        super(DBSoftwareService, self).validate()
        create = not self.instance.pk
        if create:
            account = self.get_account()
            # Validated Database
            db_user = self.get_db_user()
            try:
                DatabaseUser.objects.get(username=db_user)
            except DatabaseUser.DoesNotExist:
                raise ValidationError(
                    _("Global database user for PHPList '%(db_user)s' does not exists.") % {
                        'db_user': db_user
                    }
                )
            db = Database(name=self.get_db_name(), account=account)
            try:
                db.full_clean()
            except ValidationError as e:
                raise ValidationError({
                    'name': e.messages,
                })
    
    def save(self):
        super(DBSoftwareService, self).save()
        account = self.get_account()
        # Database
        db_name = self.get_db_name()
        db_user = self.get_db_user()
        db, db_created = account.databases.get_or_create(name=db_name, type=Database.MYSQL)
        user = DatabaseUser.objects.get(username=db_user)
        db.users.add(user)
        self.instance.database_id = db.pk
