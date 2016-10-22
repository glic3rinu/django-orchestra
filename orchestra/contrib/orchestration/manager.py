import logging
import threading
import traceback
from collections import OrderedDict

from django.core.mail import mail_admins

from orchestra.utils import db
from orchestra.utils.python import import_class, OrderedSet

from . import settings, Operation
from .backends import ServiceBackend
from .helpers import send_report
from .models import BackendLog
from .signals import pre_action, post_action, pre_commit, post_commit, pre_prepare, post_prepare


logger = logging.getLogger(__name__)
router = import_class(settings.ORCHESTRATION_ROUTER)


def keep_log(execute, log, operations):
    def wrapper(*args, **kwargs):
        """ send report """
        # Remember that threads have their oun connection poll
        # No need to EVER temper with the transaction here
        log = kwargs['log']
        try:
            log = execute(*args, **kwargs)
        except Exception as e:
            trace = traceback.format_exc()
            log.state = log.EXCEPTION
            log.stderr += trace
            log.save()
            subject = 'EXCEPTION executing backend(s) %s %s' % (args, kwargs)
            logger.error(subject)
            logger.error(trace)
            mail_admins(subject, trace)
            # We don't propagate the exception further to avoid transaction rollback
        finally:
            # Store and log the operation
            for operation in operations:
                logger.info("Executed %s" % operation)
                operation.store(log)
            if not log.is_success:
                send_report(execute, args, log)
            stdout = log.stdout.strip()
            stdout and logger.debug('STDOUT %s', stdout.encode('ascii', errors='replace').decode())
            stderr = log.stderr.strip()
            stderr and logger.debug('STDERR %s', stderr.encode('ascii', errors='replace').decode())
    return wrapper


def generate(operations):
    scripts = OrderedDict()
    cache = {}
    serialize = False
    # Generate scripts per route+backend
    for operation in operations:
        logger.debug("Queued %s" % operation)
        if operation.routes is None:
            operation.routes = router.objects.get_for_operation(operation, cache=cache)
        for route in operation.routes:
            # TODO key by action.async
            async_action = route.action_is_async(operation.action)
            key = (route, operation.backend, async_action)
            if key not in scripts:
                backend, operations = (operation.backend(), [operation])
                scripts[key] = (backend, operations)
                backend.set_head()
                pre_prepare.send(sender=backend.__class__, backend=backend)
                backend.prepare()
                post_prepare.send(sender=backend.__class__, backend=backend)
            else:
                scripts[key][1].append(operation)
            # Get and call backend action method
            backend = scripts[key][0]
            method = getattr(backend, operation.action)
            kwargs = {
                'sender': backend.__class__,
                'backend': backend,
                'instance': operation.instance,
                'action': operation.action,
            }
            backend.set_content()
            pre_action.send(**kwargs)
            method(operation.instance)
            post_action.send(**kwargs)
            if backend.serialize:
                serialize = True
    for value in scripts.values():
        backend, operations = value
        backend.set_tail()
        pre_commit.send(sender=backend.__class__, backend=backend)
        backend.commit()
        post_commit.send(sender=backend.__class__, backend=backend)
    return scripts, serialize


def execute(scripts, serialize=False, async=None):
    """
    executes the operations on the servers
    
    serialize: execute one backend at a time
    async: do not join threads (overrides route.async)
    """
    if settings.ORCHESTRATION_DISABLE_EXECUTION:
        logger.info('Orchestration execution is dissabled by ORCHESTRATION_DISABLE_EXECUTION.')
        return []
    # Execute scripts on each server
    executions = []
    threads_to_join = []
    logs = []
    for key, value in scripts.items():
        route, __, async_action = key
        backend, operations = value
        args = (route.host,)
        if async is None:
            is_async = not serialize and (route.async or async_action)
        else:
            is_async = not serialize and (async or async_action)
        kwargs = {
            'async': is_async,
        }
        # we clone the connection just in case we are isolated inside a transaction
        with db.clone(model=BackendLog) as handle:
            log = backend.create_log(*args, using=handle.target)
            log._state.db = handle.origin
        kwargs['log'] = log
        task = keep_log(backend.execute, log, operations)
        logger.debug('%s is going to be executed on %s.' % (backend, route.host))
        if serialize:
            # Execute one backend at a time, no need for threads
            task(*args, **kwargs)
        else:
            task = db.close_connection(task)
            thread = threading.Thread(target=task, args=args, kwargs=kwargs)
            thread.start()
            if not is_async:
                threads_to_join.append(thread)
        logs.append(log)
    [ thread.join() for thread in threads_to_join ]
    return logs


def collect(instance, action, **kwargs):
    """ collect operations """
    operations = kwargs.get('operations', OrderedSet())
    route_cache = kwargs.get('route_cache', {})
    for backend_cls in ServiceBackend.get_backends():
        # Check if there exists a related instance to be executed for this backend and action
        instances = []
        if action in backend_cls.actions:
            if backend_cls.is_main(instance):
                instances = [(instance, action)]
            else:
                for candidate in backend_cls.get_related(instance):
                    if candidate.__class__.__name__ == 'ManyRelatedManager':
                        if 'pk_set' in kwargs:
                            # m2m_changed signal
                            candidates = kwargs['model'].objects.filter(pk__in=kwargs['pk_set'])
                        else:
                            candidates = candidate.all()
                    else:
                        candidates = [candidate]
                    for candidate in candidates:
                        # Check if a delete for candidate is in operations
                        delete_mock = Operation(backend_cls, candidate, Operation.DELETE)
                        if delete_mock not in operations:
                            # related objects with backend.model trigger save()
                            instances.append((candidate, Operation.SAVE))
        for selected, iaction in instances:
            # Maintain consistent state of operations based on save/delete behaviour
            # Prevent creating a deleted selected by deleting existing saves
            if iaction == Operation.DELETE:
                save_mock = Operation(backend_cls, selected, Operation.SAVE)
                try:
                    operations.remove(save_mock)
                except KeyError:
                    pass
            else:
                update_fields = kwargs.get('update_fields', None)
                if update_fields is not None:
                    # TODO remove this, django does not execute post_save if update_fields=[]...
                    # Maybe open a ticket at Djangoproject ?
                    # INITIAL INTENTION: "update_fields=[]" is a convention for explicitly executing backend
                    # i.e. account.disable()
                    if update_fields != []:
                        execute = False
                        for field in update_fields:
                            if field not in backend_cls.ignore_fields:
                                execute = True
                                break
                        if not execute:
                            continue
            operation = Operation(backend_cls, selected, iaction)
            # Only schedule operations if the router has execution routes
            routes = router.objects.get_for_operation(operation, cache=route_cache)
            if routes:
                logger.debug("Operation %s collected for execution" % operation)
                operation.routes = routes
                if iaction != Operation.DELETE:
                    # usually we expect to be using last object state,
                    # except when we are deleting it
                    operations.discard(operation)
                elif iaction == Operation.DELETE:
                    operation.preload_context()
                operations.add(operation)
    return operations
