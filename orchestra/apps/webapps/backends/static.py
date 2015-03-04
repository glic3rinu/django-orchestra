from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from . import WebAppServiceMixin


class StaticBackend(WebAppServiceMixin, ServiceController):
    verbose_name = _("Static")
    directive = 'static'
    default_route_match = "webapp.type == 'static'"
    
    def save(self, webapp):
        if not self.valid_directive(webapp):
            return
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
    
    def delete(self, webapp):
        if not self.valid_directive(webapp):
            return
        context = self.get_context(webapp)
        self.delete_webapp_dir(context)
