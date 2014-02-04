from orchestra.utils import plugins

from . import methods

# TODO support for both, step based and sync based backends

class ServiceBackend(object):
    """
    Service management backend base class
    
    It uses the _unit of work_ design principle, which allows bulk operations to
    be conviniently supported. Each backend generates the configuration for all
    the changes of all modified objects, reloading the daemon just once.
    """
    name = None
    verbose_name = None
    model = None
    related_models = () # ((model, accessor__attribute),)
    method = methods.SSH
    type = 'task' # 'sync'
    
    __metaclass__ = plugins.PluginMount
    
    def __unicode__(self):
        return self.name
    
    def __init__(self):
        self.cmds = []
    
    @property
    def script(self):
        return '\n\n'.join(self.cmds)
    
    @classmethod
    def get_backends(cls):
        return cls.plugins
    
    def execute(self, server):
        self.method(server, self.script)
    
    def append(self, cmd):
        self.cmds.append(cmd)
    
    def commit(self):
        """ apply the configuration, usually reloading a service """
        pass
