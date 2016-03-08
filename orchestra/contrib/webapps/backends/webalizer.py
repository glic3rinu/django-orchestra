from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController

from . import WebAppServiceMixin


# TODO DEPRECATE
class WebalizerAppController(WebAppServiceMixin, ServiceController):
    """
    Needed for cleaning up webalizer main folder when webapp deleteion withou related contents
    """
    verbose_name = _("Webalizer App")
    default_route_match = "webapp.type == 'webalizer'"
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.delete_webapp_dir(context)
