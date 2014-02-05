from threading import local

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from . import manager
from .backends import ServiceBackend
from .operations import Operation


@receiver(post_save)
def post_save_collector(sender, *args, **kwargs):
    OperationsMiddleware.collect('save', sender, *args, **kwargs)

@receiver(post_delete)
def post_delete_collector(sender, *args, **kwargs):
    OperationsMiddleware.collect('delete', sender, *args, **kwargs)


class OperationsMiddleware(object):
    """
    Stores all the operations derived from save and delete signals and executes them
    at the end of the request/response cycle
    """
    thread_locals = local()
    
    @classmethod
    def get_pending_operations(cls):
        request = cls.thread_locals.request
        if not hasattr(request, 'pending_operations'):
            request.pending_operations = set()
        return request.pending_operations
    
    @classmethod
    def collect(cls, action, sender, *args, **kwargs):
        """ Collects all pending operations derived from model signals """
        request = getattr(cls.thread_locals, 'request', None)
        if request is None:
            return
        pending_operations = cls.get_pending_operations()
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
                pending_operations.add(Operation(backend, instance, action))
                break
    
    def process_request(self, request):
        """ Store request on a thread local variable """
        type(self).thread_locals.request = request
    
    def process_response(self, request, response):
        """ Processes pending backend operations """
        operations = [ op for op  in type(self).get_pending_operations() ]
        manager.execute(operations)
        return response
