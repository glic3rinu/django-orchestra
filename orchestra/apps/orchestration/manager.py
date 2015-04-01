import logging
import threading
import traceback
from collections import OrderedDict

from django import db
from django.core.mail import mail_admins

from orchestra.utils.python import import_class

from . import settings
from .backends import ServiceBackend
from .helpers import send_report
from .models import BackendLog, BackendOperation as Operation
from .signals import pre_action, post_action


logger = logging.getLogger(__name__)
router = import_class(settings.ORCHESTRATION_ROUTER)


def as_task(execute):
    def wrapper(*args, **kwargs):
        """ send report """
        # Tasks run on a separate transaction pool (thread), no need to temper with the transaction
        try:
            log = execute(*args, **kwargs)
            if log.state != log.SUCCESS:
                send_report(execute, args, log)
        except Exception as e:
            subject = 'EXCEPTION executing backend(s) %s %s' % (str(args), str(kwargs))
            message = traceback.format_exc()
            logger.error(subject)
            logger.error(message)
            mail_admins(subject, message)
            # We don't propagate the exception further to avoid transaction rollback
        else:
            # Using the wrapper function as threader messenger for the execute output
            # Absense of it will indicate a failure at this stage
            wrapper.log = log
            return log
    return wrapper


def close_connection(execute):
    """ Threads have their own connection pool, closing it when finishing """
    def wrapper(*args, **kwargs):
        try:
            log = execute(*args, **kwargs)
        except:
            pass
        else:
            wrapper.log = log
        finally:
            db.connection.close()
    return wrapper


def generate(operations):
    scripts = OrderedDict()
    cache = {}
    block = False
    # Generate scripts per server+backend
    for operation in operations:
        logger.debug("Queued %s" % str(operation))
        if operation.servers is None:
            operation.servers = router.get_servers(operation, cache=cache)
        for server in operation.servers:
            key = (server, operation.backend)
            if key not in scripts:
                scripts[key] = (operation.backend(), [operation])
                scripts[key][0].prepare()
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
            pre_action.send(**kwargs)
            method(operation.instance)
            post_action.send(**kwargs)
            if backend.block:
                block = True
    for value in scripts.itervalues():
        backend, operations = value
        backend.commit()
    return scripts, block


def execute(scripts, block=False, async=False):
    """ executes the operations on the servers """
    # Execute scripts on each server
    threads = []
    executions = []
    for key, value in scripts.iteritems():
        server, __ = key
        backend, operations = value
        execute = as_task(backend.execute)
        logger.debug('%s is going to be executed on %s' % (backend, server))
        if block:
            # Execute one bakend at a time, no need for threads
            execute(server, async=async)
        else:
            execute = close_connection(execute)
            thread = threading.Thread(target=execute, args=(server,), kwargs={'async': async})
            thread.start()
            threads.append(thread)
        executions.append((execute, operations))
    [ thread.join() for thread in threads ]
    logs = []
    # collect results
    for execution, operations in executions:
        # There is no log if an exception has been rised at the very end of the execution
        if hasattr(execution, 'log'):
            for operation in operations:
                logger.info("Executed %s" % str(operation))
                operation.log = execution.log
                if operation.object_id:
                    # Not all backends are call with objects saved on the database
                    operation.save()
            stdout = execution.log.stdout.strip()
            stdout and logger.debug('STDOUT %s', stdout)
            stderr = execution.log.stderr.strip()
            stderr and logger.debug('STDERR %s', stderr)
            logs.append(execution.log)
        else:
            mocked_log = BackendLog(state=BackendLog.EXCEPTION)
            logs.append(mocked_log)
    return logs


def collect(instance, action, **kwargs):
    """ collect operations """
    operations = kwargs.get('operations', set())
    route_cache = kwargs.get('route_cache', {})
    for backend_cls in ServiceBackend.get_backends():
        # Check if there exists a related instance to be executed for this backend
        instances = []
        if backend_cls.is_main(instance):
            instances = [(instance, action)]
        else:
            candidate = backend_cls.get_related(instance)
            if candidate:
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
                    delete_mock = Operation.create(backend_cls, candidate, Operation.DELETE)
                    if delete_mock not in operations:
                        # related objects with backend.model trigger save()
                        instances.append((candidate, Operation.SAVE))
        for selected, iaction in instances:
            # Maintain consistent state of operations based on save/delete behaviour
            # Prevent creating a deleted selected by deleting existing saves
            if iaction == Operation.DELETE:
                save_mock = Operation.create(backend_cls, selected, Operation.SAVE)
                try:
                    operations.remove(save_mock)
                except KeyError:
                    pass
            else:
                update_fields = kwargs.get('update_fields', None)
                if update_fields is not None:
                    # "update_fileds=[]" is a convention for explicitly executing backend
                    # i.e. account.disable()
                    if update_fields != []:
                        execute = False
                        for field in update_fields:
                            if field not in backend_cls.ignore_fields:
                                execute = True
                                break
                        if not execute:
                            continue
            operation = Operation.create(backend_cls, selected, iaction)
            # Only schedule operations if the router gives servers to execute into
            servers = router.get_servers(operation, cache=route_cache)
            if servers:
                operation.servers = servers
                if iaction != Operation.DELETE:
                    # usually we expect to be using last object state,
                    # except when we are deleting it
                    operations.discard(operation)
                elif iaction == Operation.DELETE:
                    operation.preload_context()
                operations.add(operation)
    return operations
