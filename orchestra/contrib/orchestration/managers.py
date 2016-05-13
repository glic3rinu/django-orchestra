import sys
from threading import local

from django.contrib.admin.models import LogEntry
from django.db.models.signals import pre_delete, post_save, m2m_changed
from django.dispatch import receiver
from django.utils.decorators import ContextDecorator

from orchestra.utils.python import OrderedSet

from . import manager, Operation, helpers
from .middlewares import OperationsMiddleware
from .models import BackendLog, BackendOperation


@receiver(post_save, dispatch_uid='orchestration.post_save_manager_collector')
def post_save_collector(sender, *args, **kwargs):
    if sender not in (BackendLog, BackendOperation, LogEntry):
        instance = kwargs.get('instance')
        orchestrate.collect(Operation.SAVE, **kwargs)


@receiver(pre_delete, dispatch_uid='orchestration.pre_delete_manager_collector')
def pre_delete_collector(sender, *args, **kwargs):
    if sender not in (BackendLog, BackendOperation, LogEntry):
        orchestrate.collect(Operation.DELETE, **kwargs)


@receiver(m2m_changed, dispatch_uid='orchestration.m2m_manager_collector')
def m2m_collector(sender, *args, **kwargs):
    # m2m relations without intermediary models are shit. Model.post_save is not sent and
    # by the time related.post_save is sent rel objects are not accessible via RelatedManager.all()
    if kwargs.pop('action') == 'post_add' and kwargs['pk_set']:
        orchestrate.collect(Operation.SAVE, **kwargs)


class orchestrate(ContextDecorator):
    """
    Context manager for triggering backend operations out of request-response cycle, e.g. shell
    
    with orchestrate():
        user = SystemUser.objects.get(username='rata')
        user.shell = '/dev/null'
        user.save(update_fields=('shell',))
    """
    thread_locals = local()
    thread_locals.pending_operations = None
    thread_locals.route_cache = None
    
    @classmethod
    def collect(cls, action, **kwargs):
        """ Collects all pending operations derived from model signals """
        if cls.thread_locals.pending_operations is None:
            # No active orchestrate context manager
            return
        kwargs['operations'] = cls.thread_locals.pending_operations
        kwargs['route_cache'] = cls.thread_locals.route_cache
        instance = kwargs.pop('instance')
        manager.collect(instance, action, **kwargs)
    
    def __enter__(self):
        cls = type(self)
        self.old_pending_operations = cls.thread_locals.pending_operations
        cls.thread_locals.pending_operations = OrderedSet()
        self.old_route_cache = cls.thread_locals.route_cache
        cls.thread_locals.route_cache = {}
    
    def __exit__(self, exc_type, exc_value, traceback):
        cls = type(self)
        if not exc_type:
            operations = cls.thread_locals.pending_operations
            if operations:
                scripts, serialize = manager.generate(operations)
                logs = manager.execute(scripts, serialize=serialize)
                for t, msg in helpers.get_messages(logs):
                    if t == 'error':
                        sys.stderr.write('%s: %s\n' % (t, msg))
                    else:
                        sys.stdout.write('%s: %s\n' % (t, msg))
        cls.thread_locals.pending_operations = self.old_pending_operations
        cls.thread_locals.route_cache = self.old_route_cache
