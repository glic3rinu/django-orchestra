from django.apps import AppConfig

from orchestra.core import administration


class OrchestrationConfig(AppConfig):
    name = 'orchestra.contrib.orchestration'
    verbose_name = "Orchestration"
    
    def ready(self):
        from .models import Server, Route, BackendLog
        administration.register(BackendLog, icon='scriptlog.png')
        administration.register(Server, parent=BackendLog, icon='vps.png')
        administration.register(Route, parent=BackendLog, icon='hal.png')
