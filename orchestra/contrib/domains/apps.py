from django.apps import AppConfig

from orchestra.core import services


class DomainsConfig(AppConfig):
    name = 'orchestra.contrib.domains'
    verbose_name = 'Domains'
    
    def ready(self):
        from .models import Domain
        services.register(Domain, icon='domain.png')
