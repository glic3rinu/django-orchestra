from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from . import WebAppServiceMixin


class AwstatsBackend(WebAppServiceMixin, ServiceController):
    verbose_name = _("Awstats")
