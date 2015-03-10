import pkgutil
import textwrap

from .. import settings


class WebAppServiceMixin(object):
    model = 'webapps.WebApp'
    directive = None
    
    def create_webapp_dir(self, context):
        self.append("[[ ! -e %(app_path)s ]] && CREATED=true" % context)
        self.append("mkdir -p %(app_path)s" % context)
        self.append("chown %(user)s:%(group)s %(app_path)s" % context)
    
    def set_under_construction(self, context):
        if context['under_construction_path']:
            self.append("[[ $CREATED ]] && cp -r %(under_construction_path)s %(app_path)s" % context)
    
    def delete_webapp_dir(self, context):
        self.append("rm -fr %(app_path)s" % context)
    
    def get_context(self, webapp):
        return {
            'user': webapp.get_username(),
            'group': webapp.get_groupname(),
            'app_name': webapp.name,
            'type': webapp.type,
            'app_path': webapp.get_path().rstrip('/'),
            'banner': self.get_banner(),
            'under_construction_path': settings.settings.WEBAPPS_UNDER_CONSTRUCTION_PATH
        }


for __, module_name, __ in pkgutil.walk_packages(__path__):
    # sorry for the exec(), but Import module function fails :(
    exec('from . import %s' % module_name)
