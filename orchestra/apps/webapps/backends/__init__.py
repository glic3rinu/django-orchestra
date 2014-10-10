import pkgutil
import textwrap

class WebAppServiceMixin(object):
    model = 'webapps.WebApp'
    
    def create_webapp_dir(self, context):
        self.append(textwrap.dedent("""
            path=""
            for dir in $(echo %(app_path)s | tr "/" "\n"); do
                path="${path}/${dir}"
                [ -d $path ] || {
                    mkdir "${path}"
                    chown %(user)s.%(group)s "${path}"
                }
            done
        """ % context))
    
    def delete_webapp_dir(self, context):
        self.append("rm -fr %(app_path)s" % context)
    
    def get_context(self, webapp):
        return {
            'user': webapp.account.username,
            'group': webapp.account.username,
            'app_name': webapp.name,
            'type': webapp.type,
            'app_path': webapp.get_path().rstrip('/'),
            'banner': self.get_banner(),
        }


for __, module_name, __ in pkgutil.walk_packages(__path__):
    exec('from . import %s' % module_name)
