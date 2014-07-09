from django.apps import AppConfig
from django.contrib.contenttypes import generic

from orchestra.utils import running_syncdb


class ResourcesConfig(AppConfig):
    name = 'orchestra.apps.resources'
    verbose_name = 'Resources'
    
    def ready(self):
        from .models import Resource
        # TODO execute on Resource.save()
        if not running_syncdb():
            relation = generic.GenericRelation('resources.ResourceData')
            for resources in Resource.group_by_content_type():
                model = resources[0].content_type.model_class()
                model.add_to_class('resources', relation)
