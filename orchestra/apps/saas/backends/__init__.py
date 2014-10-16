import pkgutil
import textwrap


class SaaSServiceMixin(object):
    model = 'saas.SaaS'
    # TODO Match definition support on backends (mysql) and saas
    
    def get_context(self, webapp):
        # TODO
        return {
        }


for __, module_name, __ in pkgutil.walk_packages(__path__):
    # sorry for the exec(), but Import module function fails :(
    exec('from . import %s' % module_name)
