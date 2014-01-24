from orchestra.utils import plugins


# TODO create script objects

class ServiceBackend(object):
    """
    Service management backend base class
    
    It uses the _unit of work_ design principle, which allows bulk operations to
    be supported. Each backend will generate the configuration for all the changes 
    for all the modified objects, and reload the daemon once.
    """
    name = None
    verbose_name = None
    models = []
    
    __metaclass__ = plugins.PluginMount
    
    def __init__(self):
        self.cmds = []
    
    @classmethod
    def get_backends(cls):
        return cls.plugins
    
    def append(self, cmd):
        self.cmds.append(cmd)
    
    def commit(self):
        """ apply the configuration, usually reloading a service """
        pass