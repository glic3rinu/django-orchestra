import copy

from .backends import ServiceBackend, ServiceController, replace


class Operation():
    DELETE = 'delete'
    SAVE = 'save'
    MONITOR = 'monitor'
    EXCEEDED = 'exceeded'
    RECOVERY = 'recovery'
    
    def __str__(self):
        return '%s.%s(%s)' % (self.backend, self.action, self.instance)
    
    def __hash__(self):
        """ set() """
        return hash(self.backend) + hash(self.instance) + hash(self.action)
    
    def __eq__(self, operation):
        """ set() """
        return hash(self) == hash(operation)
    
    def __init__(self, backend, instance, action, routes=None):
        self.backend = backend
        # instance should maintain any dynamic attribute until backend execution
        # deep copy is prefered over copy otherwise objects will share same atributes (queryset cache)
        self.instance = copy.deepcopy(instance)
        self.action = action
        self.routes = routes
    
    @classmethod
    def execute(cls, operations, async=False):
        from . import manager
        scripts, block = manager.generate(operations)
        return manager.execute(scripts, block=block, async=async)
    
    @classmethod
    def execute_action(cls, instance, action):
        backends = ServiceBackend.get_backends(instance=instance, action=action)
        operations = [cls(backend_cls, instance, action) for backend_cls in backends]
        return cls.execute(operations)
    
    def preload_context(self):
        """
        Heuristic
        Running get_context will prevent most of related objects do not exist errors
        """
        if self.action == self.DELETE:
            if hasattr(self.backend, 'get_context'):
                self.backend().get_context(self.instance)
    
    def store(self, log):
        from .models import BackendOperation
        return BackendOperation.objects.create(
            log=log,
            backend=self.backend.get_name(),
            instance=self.instance,
            action=self.action,
        )
