import pkgutil
import textwrap


class WebAppServiceMixin(object):
    model = 'webapps.WebApp'
    directive = None
    
    def create_webapp_dir(self, context):
        self.append("mkdir -p %(app_path)s" % context)
        self.append("chown %(user)s:%(group)s %(app_path)s" % context)
    
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
        }


for __, module_name, __ in pkgutil.walk_packages(__path__):
    # sorry for the exec(), but Import module function fails :(
    exec('from . import %s' % module_name)
