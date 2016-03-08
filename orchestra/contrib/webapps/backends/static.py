from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController

from . import WebAppServiceMixin


class StaticController(WebAppServiceMixin, ServiceController):
    """
    Static web pages.
    Only creates the webapp dir and leaves the web server the decision to execute CGIs or not.
    """
    verbose_name = _("Static")
    default_route_match = "webapp.type == 'static'"
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
        self.set_under_construction(context)
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.delete_webapp_dir(context)
