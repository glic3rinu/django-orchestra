import os

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController, replace

from .. import settings


class DokuWikiMuBackend(ServiceController):
    """
    Creates a DokuWiki site on a DokuWiki multisite installation.
    """
    verbose_name = _("DokuWiki multisite")
    model = 'webapps.WebApp'
    doc_settings = (settings,
        ('SAAS_DOKUWIKI_TEMPLATE_PATH', 'SAAS_DOKUWIKI_FARM_PATH')
    )
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.append("mkdir %(app_path)" % context)
        self.append("tar xfz %(template)s -C %(app_path)s" % context)
        self.append("chown -R www-data %(app_path)s" % context)
        # TODO move dokuwiki to user directory
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.append("rm -fr %(app_path)s" % context)
    
    def get_context(self, webapp):
        context = super(DokuWikiMuBackend, self).get_context(webapp)
        context.update({
            'template': settings.SAAS_DOKUWIKI_TEMPLATE_PATH,
            'app_path': os.path.join(settings.SAAS_DOKUWIKI_FARM_PATH, webapp.name)
        })
        return replace(context, "'", '"')
