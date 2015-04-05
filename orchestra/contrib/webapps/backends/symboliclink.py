from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController, replace

from . import WebAppServiceMixin


class SymbolicLinkBackend(WebAppServiceMixin, ServiceController):
    verbose_name = _("Symbolic link webapp")
    model = 'webapps.WebApp'
    default_route_match = "webapp.type == 'symbolic-link'"
    
    def save(self, webapp):
        context = self.get_context(webapp)
        self.append("ln -s '%(link_path)s' %(app_path)s" % context)
        self.append("chown -h %(user)s:%(group)s %(app_path)s" % context)
    
    def delete(self, webapp):
        context = self.get_context(webapp)
        self.delete_webapp_dir(context)
    
    def get_context(self, webapp):
        context = super(SymbolicLinkBackend, self).get_context(webapp)
        context.update({
            'link_path': webapp.data['path'],
        })
        return replace(context, "'", '"')
