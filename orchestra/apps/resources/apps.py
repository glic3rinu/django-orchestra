from django.apps import AppConfig

from orchestra.utils import running_syncdb


class ResourcesConfig(AppConfig):
    name = 'orchestra.apps.resources'
    verbose_name = 'Resources'
    
    def ready(self):
        if not running_syncdb():
            from .models import create_resource_relation
            create_resource_relation()
