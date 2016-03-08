import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceController, replace

from .php import PHPController


class SymbolicLinkController(PHPController, ServiceController):
    """
    Same as PHPController but allows you to have the webapps on a directory diferent than the webapps dir.
    """
    verbose_name = _("Symbolic link webapp")
    model = 'webapps.WebApp'
    default_route_match = "webapp.type == 'symbolic-link'"
    
    def create_webapp_dir(self, context):
        self.append(textwrap.dedent("""\
            if [[ ! -e %(app_path)s ]]; then
                ln -s '%(link_path)s' %(app_path)s
            fi
            chown -h %(user)s:%(group)s %(app_path)s
            """) % context
        )
    
    def set_under_construction(self, context):
        pass
    
    def get_context(self, webapp):
        context = super(SymbolicLinkController, self).get_context(webapp)
        context.update({
            'link_path': webapp.data['path'],
        })
        return replace(context, "'", '"')
