import sys

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from orchestra.core import services


class SystemUsersConfig(AppConfig):
    name = 'orchestra.contrib.systemusers'
    verbose_name = "System users"
    
    def ready(self):
        from .models import SystemUser
        services.register(SystemUser, icon='roleplaying.png')
        if 'migrate' in sys.argv and 'accounts' not in sys.argv:
            post_migrate.connect(self.create_initial_systemuser,
                dispatch_uid="orchestra.contrib.systemusers.apps.create_initial_systemuser")
    
    def create_initial_systemuser(self, **kwargs):
        from .models import SystemUser
        Account = SystemUser.account.field.remote_field.model
        for account in Account.objects.filter(is_superuser=True, main_systemuser_id__isnull=True):
            systemuser = SystemUser.objects.create(username=account.username,
                password=account.password, account=account)
            account.main_systemuser = systemuser
            account.save()
            sys.stdout.write("Created initial systemuser %s.\n" % systemuser.username)
