import os
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController, replace

from .. import settings


class DrupalMuBackend(ServiceController):
    """
    Creates a Drupal site on a Drupal multisite installation
    """
    verbose_name = _("Drupal multisite")
    model = 'webapps.WebApp'
    doc_settings = (settings,
        ('SAAS_DRUPAL_SITES_PATH',)
    )
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.append(textwrap.dedent("""\
            mkdir %(drupal_path)s
            chown -R www-data %(drupal_path)s
            
            # the following assumes settings.php to be previously configured
            REGEX='^\s*$databases\[.default.\]\[.default.\]\[.prefix.\]'
            CONFIG='$databases[\'default\'][\'default\'][\'prefix\'] = \'%(app_name)s_\';'
            if [[ ! $(grep $REGEX %(drupal_settings)s) ]]; then
               echo $CONFIG >> %(drupal_settings)s
            fi""") % context
        )
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.append("rm -fr %(app_path)s" % context)
    
    def get_context(self, webapp):
        context = super(DrupalMuBackend, self).get_context(webapp)
        context['drupal_path'] = settings.SAAS_DRUPAL_SITES_PATH % context
        context['drupal_settings'] = os.path.join(context['drupal_path'], 'settings.php')
        return replace(context, "'", '"')
