from threading import local

from django.contrib.admin.models import LogEntry
from django.core.urlresolvers import resolve
from django.db import transaction
from django.db.models.signals import pre_delete, post_save, m2m_changed
from django.dispatch import receiver
from django.http.response import HttpResponseServerError

from orchestra.utils.python import OrderedSet

from . import manager, Operation
from .helpers import message_user
from .models import BackendLog, BackendOperation


@receiver(post_save, dispatch_uid='orchestration.post_save_collector')
def post_save_collector(sender, *args, **kwargs):
    if sender not in (BackendLog, BackendOperation, LogEntry):
        instance = kwargs.get('instance')
        OperationsMiddleware.collect(Operation.SAVE, **kwargs)


@receiver(pre_delete, dispatch_uid='orchestration.pre_delete_collector')
def pre_delete_collector(sender, *args, **kwargs):
    if sender not in (BackendLog, BackendOperation, LogEntry):
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
    
    It also works as a transaction middleware, making requets to run within an atomic block.
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
    
    def enter_transaction_management(self):
        type(self).thread_locals.transaction = transaction.atomic()
        type(self).thread_locals.transaction.__enter__()
    
    def leave_transaction_management(self, exception=None):
        locals = type(self).thread_locals
        if hasattr(locals, 'transaction'):
            # Don't fucking know why sometimes thread_locals does not contain a transaction
            locals.transaction.__exit__(exception, None, None)
    
    def process_request(self, request):
        """ Store request on a thread local variable """
        type(self).thread_locals.request = request
        self.enter_transaction_management()
    
    def process_exception(self, request, exception):
        """Rolls back the database and leaves transaction management"""
        self.leave_transaction_management(exception)
    
    def process_response(self, request, response):
        """ Processes pending backend operations """
        if response.status_code != 500:
            operations = self.get_pending_operations()
            if operations:
                try:
                    scripts, serialize = manager.generate(operations)
                except Exception as exception:
                    self.leave_transaction_management(exception)
                    raise
                # We commit transaction just before executing operations
                # because here is when IntegrityError show up
                self.leave_transaction_management()
                logs = manager.execute(scripts, serialize=serialize)
                if logs and resolve(request.path).app_name == 'admin':
                    message_user(request, logs)
                return response
        self.leave_transaction_management()
        return response
