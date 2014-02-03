#import Queue

from orchestra.core.middlewares import threadlocal

from .backends import ServiceBackend


class Operation(object):
    def __init__(self, backend, obj, action):
        self.backend = backend
        self.obj = obj
        self.action = action


def collect(action, sender, *args, **kwargs):
#    global pending_operations
    request = threadlocal.get_request()
    if request is None:
        return
    collection = []
    for backend in ServiceBackend.get_backends():
        for model in backend.models:
            opts = sender._meta
            if model == '%s.%s' % (opts.app_label, opts.object_name):
                if not hasattr(request, 'pending_operations'):
                    request.pending_operations = []
                operation = Operation(backend, kwargs['instance'], action)
#                pending_operations.put(operation)
                request.pending_operations.append(operation)
                break


def iterator():
    request = threadlocal.get_request()
    if request is not None and hasattr(request, 'pending_operations'):
        return iter(request.pending_operations)
    return iter([])


#def iterator():
#    global pending_operations
#    try:
#        yield pending_operations.get_nowait()
#    except Queue.Empty:
#        return


# This thread-safe global variable stores all the pending backend operations
# Operations are added to the queue during the request/response cycle
# Operations are removed by a ProcessPendingOperations middleware
# pending_operations = Queue.Queue()

