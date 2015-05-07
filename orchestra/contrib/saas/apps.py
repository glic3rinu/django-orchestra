from django.apps import AppConfig

from orchestra.core import services


class SaaSConfig(AppConfig):
    name = 'orchestra.contrib.saas'
    verbose_name = 'Saas'
    
    def ready(self):
        from . import signals
        from .models import SaaS
        services.register(SaaS, icon='saas.png')
