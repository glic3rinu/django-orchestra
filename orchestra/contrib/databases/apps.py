from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services


class DatabasesConfig(AppConfig):
    name = 'orchestra.contrib.databases'
    verbose_name = 'Databases'
    
    def ready(self):
        from .models import Database, DatabaseUser
        services.register(Database, icon='database.png')
        services.register(DatabaseUser, icon='postgresql.png', verbose_name_plural=_("Database users"))
