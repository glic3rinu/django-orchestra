from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _

from .management import create_initial_superuser


class AccountConfig(AppConfig):
    name = 'orchestra.contrib.accounts'
    verbose_name = _("Accounts")
    
    def ready(self):
        post_migrate.connect(create_initial_superuser,
            dispatch_uid="orchestra.contrib.accounts.management.createsuperuser")
