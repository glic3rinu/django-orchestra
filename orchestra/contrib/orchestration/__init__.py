import collections
import copy

from orchestra.utils.python import AttrDict

from .backends import ServiceBackend, ServiceController, replace


default_app_config = 'orchestra.contrib.orchestration.apps.OrchestrationConfig'


class Operation():
    DELETE = 'delete'
    SAVE = 'save'
    MONITOR = 'monitor'
    EXCEEDED = 'exceeded'
    RECOVERY = 'recovery'
    
    def __str__(self):
        return '%s.%s(%s)' % (self.backend, self.action, self.instance)
    
    def __repr__(self):
        return str(self)
    
    def __hash__(self):
        """ set() """
        return hash((self.backend, self.instance, self.action))
    
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
    def execute(cls, operations, serialize=False, async=None):
        from . import manager
        scripts, backend_serialize = manager.generate(operations)
        return manager.execute(scripts, serialize=(serialize or backend_serialize), async=async)
    
    @classmethod
    def create_for_action(cls, instances, action):
        if not isinstance(instances, collections.Iterable):
            instances = [instances]
        operations = []
        for instance in instances:
            backends = ServiceBackend.get_backends(instance=instance, action=action)
            for backend_cls in backends:
                operations.append(
                    cls(backend_cls, instance, action)
                )
        return operations
    
    @classmethod
    def execute_action(cls, instances, action):
        """ instances can be an object or an iterable for batch processing """
        operations = cls.create_for_action(instances, action)
        return cls.execute(operations)
    
    def preload_context(self):
        """
        Heuristic: Running get_context will prevent most of related objects do not exist errors
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
    
    @classmethod
    def load(cls, operation, log=None):
        routes = None
        if log:
            routes = {
                (operation.backend, operation.action): AttrDict(host=log.server)
            }
        return cls(operation.backend_class, operation.instance, operation.action, routes=routes)
    
