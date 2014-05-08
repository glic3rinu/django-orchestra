from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceBackend

from . import WebAppServiceMixin


class AwstatsBackend(WebAppServiceMixin, ServiceBackend):
    verbose_name = _("Awstats")
    
    def save(self, webapp):
        pass
