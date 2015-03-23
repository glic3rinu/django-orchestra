import logging
import threading
import traceback
from collections import OrderedDict

from django import db
from django.core.mail import mail_admins

from orchestra.utils.python import import_class

from . import settings
from .helpers import send_report
from .models import BackendLog
from .signals import pre_action, post_action


logger = logging.getLogger(__name__)
router = import_class(settings.ORCHESTRATION_ROUTER)


def as_task(execute):
    def wrapper(*args, **kwargs):
        """ send report """
        # Tasks run on a separate transaction pool (thread), no need to temper with the transaction
        log = execute(*args, **kwargs)
        if log.state != log.SUCCESS:
            send_report(execute, args, log)
        return log
    return wrapper


def close_connection(execute):
    """ Threads have their own connection pool, closing it when finishing """
    def wrapper(*args, **kwargs):
        try:
            log = execute(*args, **kwargs)
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
        finally:
            db.connection.close()
    return wrapper


def execute(operations, async=False):
    """ generates and executes the operations on the servers """
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
    # Execute scripts on each server
    threads = []
    executions = []
    for key, value in scripts.iteritems():
        server, __ = key
        backend, operations = value
        backend.commit()
        execute = as_task(backend.execute)
        execute = close_connection(execute)
        # DEBUG: substitute all thread related stuff for this function
        #execute(server, async=async)
        logger.debug('%s is going to be executed on %s' % (backend, server))
        thread = threading.Thread(target=execute, args=(server,), kwargs={'async': async})
        thread.start()
        if block:
            thread.join()
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
