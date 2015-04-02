from threading import local

from django.core.urlresolvers import resolve
from django.db import connection, transaction
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
    
    It also works as a transaction middleware. Each view function will be run
    with commit_on_response activated - that way a save() doesn't do a direct
    commit, the commit is done when a successful response is created. If an
    exception happens, the database is rolled back.
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
    
    def commit_transaction(self):
        if not transaction.get_autocommit():
            if transaction.is_dirty():
                # Note: it is possible that the commit fails. If the reason is
                # closed connection or some similar reason, then there is
                # little hope to proceed nicely. However, in some cases (
                # deferred foreign key checks for exampl) it is still possible
                # to rollback().
                try:
                    transaction.commit()
                except Exception:
                    # If the rollback fails, the transaction state will be
                    # messed up. It doesn't matter, the connection will be set
                    # to clean state after the request finishes. And, we can't
                    # clean the state here properly even if we wanted to, the
                    # connection is in transaction but we can't rollback...
                    transaction.rollback()
                    transaction.leave_transaction_management()
                    raise
            transaction.leave_transaction_management()
    
    def process_request(self, request):
        """ Store request on a thread local variable """
        type(self).thread_locals.request = request
        # Enters transaction management
        transaction.enter_transaction_management()
    
    def process_exception(self, request, exception):
        """Rolls back the database and leaves transaction management"""
        if transaction.is_dirty():
            # This rollback might fail because of network failure for example.
            # If rollback isn't possible it is impossible to clean the
            # connection's state. So leave the connection in dirty state and
            # let request_finished signal deal with cleaning the connection.
            transaction.rollback()
        transaction.leave_transaction_management()
    
    def process_response(self, request, response):
        """ Processes pending backend operations """
        if not isinstance(response, HttpResponseServerError):
            operations = type(self).get_pending_operations()
            if operations:
                scripts, block = manager.generate(operations)
                # We commit transaction just before executing operations
                # because here is when IntegrityError show up
                self.commit_transaction()
                logs = manager.execute(scripts, block=block)
                if logs and resolve(request.path).app_name == 'admin':
                    message_user(request, logs)
                return response
        self.commit_transaction()
        return response
