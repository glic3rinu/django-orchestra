from django.apps import AppConfig

from orchestra.utils import database_ready


class ResourcesConfig(AppConfig):
    name = 'orchestra.apps.resources'
    verbose_name = 'Resources'
    
    def ready(self):
        if database_ready():
            from .models import create_resource_relation
            create_resource_relation()
    
    def reload_relations(self):
        from .admin import insert_resource_inlines
        from .models import create_resource_relation
        from .serializers import insert_resource_serializers
        insert_resource_inlines()
        insert_resource_serializers()
        create_resource_relation()
