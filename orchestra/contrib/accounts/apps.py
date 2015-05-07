from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services, accounts


class AccountConfig(AppConfig):
    name = 'orchestra.contrib.accounts'
    verbose_name = _("Accounts")
    
    def ready(self):
        from .management import create_initial_superuser
        from .models import Account
        services.register(Account, menu=False, dashboard=False)
        accounts.register(Account, icon='Face-monkey.png')
        post_migrate.connect(create_initial_superuser,
            dispatch_uid="orchestra.contrib.accounts.management.createsuperuser")
