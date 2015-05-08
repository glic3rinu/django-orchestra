from django.apps import AppConfig

from orchestra.core import administration, accounts, services
from orchestra.core.translations import ModelTranslation


class PlansConfig(AppConfig):
    name = 'orchestra.contrib.plans'
    verbose_name = 'Plans'
    
    def ready(self):
        from .models import Plan, ContractedPlan
        accounts.register(ContractedPlan, icon='ContractedPack.png')
        services.register(ContractedPlan, menu=False, dashboard=False)
        administration.register(Plan, icon='Pack.png')
        ModelTranslation.register(Plan, ('verbose_name',))
