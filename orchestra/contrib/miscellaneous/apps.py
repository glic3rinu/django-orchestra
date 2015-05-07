from django.apps import AppConfig

from orchestra.core import services, administration
from orchestra.core.translations import ModelTranslation


class MiscellaneousConfig(AppConfig):
    name = 'orchestra.contrib.miscellaneous'
    verbose_name = 'Miscellaneous'
    
    def ready(self):
        from .models import MiscService, Miscellaneous
        services.register(Miscellaneous, icon='applications-other.png')
        administration.register(MiscService, icon='Misc-Misc-Box-icon.png')
        ModelTranslation.register(MiscService, ('verbose_name',))
