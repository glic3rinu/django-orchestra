from threading import local

from django.core.urlresolvers import resolve
from django.db.models.signals import pre_delete, post_save, m2m_changed
from django.dispatch import receiver
from django.http.response import HttpResponseServerError

from orchestra.utils.python import OrderedSet

from .backends import ServiceBackend
from .helpers import message_user
from .models import BackendLog
from .models import BackendOperation as Operation


@receiver(post_save, dispatch_uid='orchestration.post_save_collector')
def post_save_collector(sender, *args, **kwargs):
    if sender not in [BackendLog, Operation]:
        OperationsMiddleware.collect(Operation.SAVE, **kwargs)

@receiver(pre_delete, dispatch_uid='orchestration.pre_delete_collector')
def pre_delete_collector(sender, *args, **kwargs):
    if sender not in [BackendLog, Operation]:
        OperationsMiddleware.collect(Operation.DELETE, **kwargs)

@receiver(m2m_changed, dispatch_uid='orchestration.m2m_collector')
def m2m_collector(sender, *args, **kwargs):
    # m2m relations without intermediary models are shit. Model.post_save is not sent and
    # by the time related.post_save is sent rel objects are not accessible via RelatedManager.all()
    # We have to use this inefficient technique of collecting the instances via m2m_changed.post_add
    if kwargs.pop('action') == 'post_add' and kwargs['pk_set']:
        for instance in kwargs['model'].objects.filter(pk__in=kwargs['pk_set']):
            kwargs['instance'] = instance
            OperationsMiddleware.collect(Operation.SAVE, **kwargs)


class OperationsMiddleware(object):
    """
    Stores all the operations derived from save and delete signals and executes them
    at the end of the request/response cycle
    """
    # Thread local is used because request object is not available on model signals
    thread_locals = local()
    
    @classmethod
    def get_pending_operations(cls):
        # Check if an error poped up before OperationsMiddleware.process_request()
        if hasattr(cls.thread_locals, 'request'):
            request = cls.thread_locals.request
            if not hasattr(request, 'pending_operations'):
                request.pending_operations = OrderedSet()
            return request.pending_operations
        return set()
    
    @classmethod
    def collect(cls, action, **kwargs):
        """ Collects all pending operations derived from model signals """
        request = getattr(cls.thread_locals, 'request', None)
        if request is None:
            return
        pending_operations = cls.get_pending_operations()
        for backend in ServiceBackend.get_backends():
            # Check if there exists a related instance to be executed for this backend
            instances = []
            if backend.is_main(kwargs['instance']):
                instances = [(kwargs['instance'], action)]
            else:
                candidate = backend.get_related(kwargs['instance'])
                if candidate:
                    if candidate.__class__.__name__ == 'ManyRelatedManager':
                        candidates = candidate.all()
                    else:
                        candidates = [candidate]
                    for candidate in candidates:
                        # Check if a delete for candidate is in pending_operations
                        delete = Operation.create(backend, candidate, Operation.DELETE)
                        if delete not in pending_operations:
                            # related objects with backend.model trigger save()
                            action = Operation.SAVE
                            instances.append((candidate, action))
            for instance, action in instances:
                # Maintain consistent state of pending_operations based on save/delete behaviour
                # Prevent creating a deleted instance by deleting existing saves
                if action == Operation.DELETE:
                    save = Operation.create(backend, instance, Operation.SAVE)
                    try:
                        pending_operations.remove(save)
                    except KeyError:
                        pass
                else:
                    update_fields = kwargs.get('update_fields', None)
                    if update_fields:
                        # "update_fileds=[]" is a convention for explicitly executing backend
                        # i.e. account.disable()
                        if update_fields != []:
                            execute = False
                            for field in update_fields:
                                if field not in backend.ignore_fields:
                                    execute = True
                                    break
                            if not execute:
                                continue
                operation = Operation.create(backend, instance, action)
                if action != Operation.DELETE:
                    # usually we expect to be using last object state,
                    # except when we are deleting it
                    pending_operations.discard(operation)
                pending_operations.add(operation)
    
    def process_request(self, request):
        """ Store request on a thread local variable """
        type(self).thread_locals.request = request
    
    def process_response(self, request, response):
        """ Processes pending backend operations """
        if not isinstance(response, HttpResponseServerError):
            operations = type(self).get_pending_operations()
            if operations:
                logs = Operation.execute(operations)
                if logs and resolve(request.path).app_name == 'admin':
                    message_user(request, logs)
        return response
