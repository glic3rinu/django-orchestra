from django.apps import AppConfig

from orchestra.core import services
from orchestra.utils.db import database_ready


class WebsitesConfig(AppConfig):
    name =  'orchestra.contrib.websites'
    
    def ready(self):
        if database_ready():
#            from django.contrib.contenttypes.models import ContentType
#            from .models import Content, Website
#            qset = Content.content_type.field.get_limit_choices_to()
#            for ct in ContentType.objects.filter(qset):
#                relation = GenericRelation('websites.Content')
#                ct.model_class().add_to_class('content_set', relation)
            from .models import Website
            services.register(Website, icon='Applications-internet.png')
