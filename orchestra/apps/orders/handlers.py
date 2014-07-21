from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from orchestra.utils import plugins


class ServiceHandler(plugins.Plugin):
    model = None
    
    __metaclass__ = plugins.PluginMount
    
    def __init__(self, service):
        self.service = service
    
    @classmethod
    def get_plugin_choices(cls):
        choices = super(ServiceHandler, cls).get_plugin_choices()
        return [('', _("Default"))] + choices
    
    def __getattr__(self, attr):
        return getattr(self.service, attr)
    
    def matches(self, instance):
        safe_locals = {
            instance._meta.model_name: instance
        }
        return eval(self.match, safe_locals)
    
    def get_metric(self, instance):
        safe_locals = {
            instance._meta.model_name: instance
        }
        return eval(self.metric, safe_locals)
    
    def get_content_type(self):
        if not self.model:
            return self.content_type
        app_label, model = self.model.split('.')
        return ContentType.objects.get_by_natural_key(app_label, model.lower())
