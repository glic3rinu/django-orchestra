import Queue

from .backends import ServiceBackend


class Operation(object):
    def __init__(self, backend, obj, action):
        self.backend = backend
        self.obj = obj
        self.action = action


def collect(action, sender, *args, **kwargs):
    global pending_operations
    collection = []
    for backend in ServiceBackend.get_backends():
        for model in backend.models:
            opts = sender._meta
            if model == '%s.%s' % (opts.app_label, opts.object_name):
                pending_operations.put(Operation(backend, kwargs['instance'], action))
                break


def iterator():
    global pending_operations
    try:
        yield pending_operations.get_nowait()
    except Queue.Empty:
        return


# This thread-safe global variable stores all the pending backend operations
# Operations are added to the list during the request/response cycle
# Operations are removed by a ProcessPendingOperations middleware
pending_operations = Queue.Queue()
