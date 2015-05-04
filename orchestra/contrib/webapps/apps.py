from django.apps import AppConfig

from orchestra.core import services


class WebAppsConfig(AppConfig):
    name = 'orchestra.contrib.webapps'
    verbose_name = 'Webapps'
    
    def ready(self):
        from . import signals
        from .models import WebApp
        services.register(WebApp)
