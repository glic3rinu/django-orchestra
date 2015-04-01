from threading import local

from django.core.urlresolvers import resolve
from django.db.models.signals import pre_delete, post_save, m2m_changed
from django.dispatch import receiver
from django.http.response import HttpResponseServerError

from orchestra.utils.python import OrderedSet

from . import manager
from .helpers import message_user
from .models import BackendLog, BackendOperation as Operation


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
    if kwargs.pop('action') == 'post_add' and kwargs['pk_set']:
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
    def get_route_cache(cls):
        """ chache the routes to save sql queries """
        if hasattr(cls.thread_locals, 'request'):
            request = cls.thread_locals.request
            if not hasattr(request, 'route_cache'):
                request.route_cache = {}
            return request.route_cache
        return {}
    
    @classmethod
    def collect(cls, action, **kwargs):
        """ Collects all pending operations derived from model signals """
        request = getattr(cls.thread_locals, 'request', None)
        if request is None:
            return
        kwargs['operations'] = cls.get_pending_operations()
        kwargs['route_cache'] = cls.get_route_cache()
        instance = kwargs.pop('instance')
        manager.collect(instance, action, **kwargs)
    
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
