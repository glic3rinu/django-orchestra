from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceBackend

from . import WebAppServiceMixin


class StaticBackend(WebAppServiceMixin, ServiceBackend):
    verbose_name = _("Static")
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.create_webapp_dir(context)
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.delete_webapp_dir(context)
