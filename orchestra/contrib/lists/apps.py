from django.apps import AppConfig

from orchestra.core import services


class ListsConfig(AppConfig):
    name = 'orchestra.contrib.lists'
    verbose_name = 'Lists'
    
    def ready(self):
        from .models import List
        services.register(List, icon='email-alter.png')
        from . import signals
