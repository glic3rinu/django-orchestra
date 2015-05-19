from django.apps import AppConfig

from orchestra.core import administration
from orchestra.core.translations import ModelTranslation


class ServicesConfig(AppConfig):
    name = 'orchestra.contrib.services'
    verbose_name = 'Services'

    def ready(self):
        from .models import Service
        administration.register(Service, icon='price.png')
        ModelTranslation.register(Service, ('description',))
