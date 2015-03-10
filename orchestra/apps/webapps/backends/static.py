from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from . import WebAppServiceMixin


class StaticBackend(WebAppServiceMixin, ServiceController):
    verbose_name = _("Static")
    default_route_match = "webapp.type == 'static'"
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
        self.set_under_construction(context)
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.delete_webapp_dir(context)
