from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra import plugins
from orchestra.contrib.databases.models import Database, DatabaseUser
from orchestra.contrib.orchestration import Operation
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from .. import settings
from ..forms import SaaSPasswordForm


class SoftwareService(plugins.Plugin):
    form = SaaSPasswordForm
    site_domain = None
    has_custom_domain = False
    icon = 'orchestra/icons/apps.png'
    class_verbose_name = _("Software as a Service")
    plugin_field = 'service'
    
    @classmethod
    @cached
    def get_plugins(cls):
        plugins = []
        for cls in settings.SAAS_ENABLED_SERVICES:
            plugins.append(import_class(cls))
        return plugins
    
    def get_change_readonly_fileds(cls):
        fields = super(SoftwareService, cls).get_change_readonly_fileds()
        return fields + ('name',)
    
    def get_site_domain(self):
        context = {
            'site_name': self.instance.name,
            'name': self.instance.name,
        }
        return self.site_domain % context
    
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
    
    def save(self):
        pass
    
    def delete(self):
        pass
    
    def get_related(self):
        return []


class DBSoftwareService(SoftwareService):
    db_name = None
    db_user = None
    
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
        account_model = self.instance._meta.get_field_by_name('account')[0]
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
        account = self.get_account()
        # Database
        db_name = self.get_db_name()
        db_user = self.get_db_user()
        db, db_created = account.databases.get_or_create(name=db_name, type=Database.MYSQL)
        user = DatabaseUser.objects.get(username=db_user)
        db.users.add(user)
        self.instance.database_id = db.pk
