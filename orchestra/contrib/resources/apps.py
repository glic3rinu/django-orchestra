from django import db
from django.apps import AppConfig

from orchestra.core import administration
from orchestra.utils.db import database_ready


class ResourcesConfig(AppConfig):
    name = 'orchestra.contrib.resources'
    verbose_name = 'Resources'
    
    def ready(self):
        if database_ready():
            from .models import create_resource_relation
            try:
                create_resource_relation()
            except db.utils.OperationalError:
                # Not ready afterall
                pass
        from .models import Resource, ResourceData, MonitorData
        administration.register(Resource, icon='gauge.png')
        administration.register(ResourceData, parent=Resource, icon='monitor.png')
        administration.register(MonitorData, parent=Resource, dashboard=False)
        from . import signals
    
    def reload_relations(self):
        from .admin import insert_resource_inlines
        from .models import create_resource_relation
        from .serializers import insert_resource_serializers
        insert_resource_inlines()
        insert_resource_serializers()
        create_resource_relation()
