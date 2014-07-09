from orchestra.apps.orchestration import ServiceBackend


class ServiceMonitor(ServiceBackend):
    TRAFFIC = 'traffic'
    DISK = 'disk'
    MEMORY = 'memory'
    CPU = 'cpu'
    
    actions = ('monitor', 'resource_exceeded', 'resource_recovery')
    
    @classmethod
    def get_backends(cls):
        """ filter monitor classes """
        return [plugin for plugin in cls.plugins if ServiceMonitor in plugin.__mro__]
    
    def store(self, stdout):
        """ object_id value """
        for line in stdout.readlines():
            line = line.strip()
            object_id, value = line.split()
            # TODO date
            MonitorHistory.store(self.model, object_id, value, date)
    
    def execute(self, server):
        log = super(MonitorBackend, self).execute(server)
        return log
