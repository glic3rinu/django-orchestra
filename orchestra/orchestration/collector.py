from .backends import ServiceBackend
from .middlewares import OperationsMiddleware


class Operation(object):
    """
    Encapsulates an operation,
    storing its related object, the action and the backend.
    """
    def __init__(self, backend, instance, action):
        self.backend = backend
        self.instance = instance
        self.action = action
    
    def __hash__(self):
        return hash(self.backend) + hash(self.instance) + hash(self.action)
    
    def __eq__(self, operation):
        return hash(self) == hash(operation)


def collect(action, sender, *args, **kwargs):
    """ collects pending operations into a _unit of work_ """
    request = OperationsMiddleware.get_request()
    if request is None:
        return
    collection = []
    instance = None
    for backend in ServiceBackend.get_backends():
        opts = sender._meta
        model = '%s.%s' % (opts.app_label, opts.object_name)
        if backend.model == model:
            instance = kwargs['instance']
        else:
            for rel_model, attribute in backend.related_models:
                if rel_model == model:
                    instance = getattr(kwargs['instance'], attribute)
                    break
        if instance is not None:
            if not hasattr(request, 'pending_operations'):
                request.pending_operations = set()
            request.pending_operations.add(Operation(backend, instance, action))
            break


def iterator():
    request = OperationsMiddleware.get_request()
    if request is not None and hasattr(request, 'pending_operations'):
        return iter(request.pending_operations)
    return iter([])
