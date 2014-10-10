import copy
from threading import local

from django.core.urlresolvers import resolve
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.http.response import HttpResponseServerError

from orchestra.utils.python import OrderedSet

from .backends import ServiceBackend
from .helpers import message_user
from .models import BackendLog
from .models import BackendOperation as Operation


@receiver(post_save, dispatch_uid='orchestration.post_save_collector')
def post_save_collector(sender, *args, **kwargs):
    if sender != BackendLog:
        OperationsMiddleware.collect(Operation.SAVE, **kwargs)

@receiver(pre_delete, dispatch_uid='orchestration.pre_delete_collector')
def pre_delete_collector(sender, *args, **kwargs):
    if sender != BackendLog:
        OperationsMiddleware.collect(Operation.DELETE, **kwargs)


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
        good_action = action
        pending_operations = cls.get_pending_operations()
        for backend in ServiceBackend.get_backends():
            instance = None
            if backend.is_main(kwargs['instance']):
                instance = kwargs['instance']
            else:
                candidate = backend.get_related(kwargs['instance'])
                if candidate:
                    delete = Operation.create(backend, candidate, Operation.DELETE)
                    if delete not in pending_operations:
                        instance = candidate
                        # related objects with backend.model trigger save()
                        action = Operation.SAVE
            if instance is not None:
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
                instance = copy.copy(instance)
                good = instance
                operation = Operation.create(backend, instance, action)
                if action != Operation.DELETE:
                    # usually we expect to be using last object state,
                    # except when we are deleting it
                    pending_operations.discard(operation)
                pending_operations.add(operation)
        try:
            print kwargs['instance'], good_action
        except:
            pass

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
