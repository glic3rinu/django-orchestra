import pkgutil


class WebAppServiceMixin(object):
    model = 'webapps.WebApp'
    
    def create_webapp_dir(self, context):
        self.append("mkdir -p '%(app_path)s'" % context)
        self.append("chown %(user)s.%(group)s '%(app_path)s'" % context)
    
    def delete_webapp_dir(self, context):
        self.append("rm -fr %(app_path)s" % context)
    
    def get_context(self, webapp):
        return {
            'user': webapp.account.user.username,
            'group': webapp.account.user.username,
            'app_name': webapp.name,
            'type': webapp.type,
            'app_path': webapp.get_path(),
            'banner': self.get_banner(),
        }


for __, module_name, __ in pkgutil.walk_packages(__path__):
    exec('from . import %s' % module_name)
