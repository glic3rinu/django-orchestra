import os

from django.utils.translation import ugettext_lazy as _

from orchestra.apps.orchestration import ServiceController

from . import WebAppServiceMixin
from .. import settings


class DrupalMuBackend(WebAppServiceMixin, ServiceController):
    verbose_name = _("Drupal multisite")
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.append("mkdir %(drupal_path)s" % context)
        self.append("chown -R www-data %(drupal_path)s" % context)
        self.append(
            "# the following assumes settings.php to be previously configured\n"
            "REGEX='^\s*$databases\[.default.\]\[.default.\]\[.prefix.\]'\n"
            "CONFIG='$databases[\'default\'][\'default\'][\'prefix\'] = \'%(app_name)s_\';'\n"
            "if [[ ! $(grep $REGEX %(drupal_settings)s) ]]; then\n"
            "   echo $CONFIG >> %(drupal_settings)s\n"
            "fi" % context
        )
    
    def selete(self, webapp):
        context = self.get_context(webapp)
        self.append("rm -fr %(app_path)s" % context)
    
    def get_context(self, webapp):
        context = super(DrupalMuBackend, self).get_context(webapp)
        context['drupal_path'] = settings.WEBAPPS_DRUPAL_SITES_PATH % context
        context['drupal_settings'] = os.path.join(context['drupal_path'], 'settings.php')
        return context
