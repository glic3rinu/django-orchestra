from orchestra.utils import plugins


# TODO create script objects

class ServiceBackend(object):
    """
    Service management backend base class
    
    It uses the _unit of work_ design principle, which allows bulk operations to
    be conviniently supported. Each backend generates the configuration for all
    the changes of all modified objects, reloading the daemon just once.
    
    Execution steps:
        1. Collect all save and delete model signals of an HTTP request
        2. Find related daemon instances using the routing backend
        3. Generate per instance scripts
        4. Send the task to Celery just before commiting the transacion to the DB
           Make sure Celery will execute the scripts in FIFO order (single process?)
    """
    name = None
    verbose_name = None
    models = []
    
    __metaclass__ = plugins.PluginMount
    
    def __unicode__(self):
        return self.name
    
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


# This global variable stores all the pending backend operations
# Operations are added to the list during the request/response cycle
# Operations are removed by a ExecutePendingOperations middleware
PENDING_OPERATIONS = []
