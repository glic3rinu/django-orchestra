from django.apps import AppConfig

from orchestra.core import services


class VPSConfig(AppConfig):
    name = 'orchestra.contrib.vps'
    verbose_name = 'VPS'
    
    def ready(self):
        from .models import VPS
        services.register(VPS, icon='TuxBox.png')
