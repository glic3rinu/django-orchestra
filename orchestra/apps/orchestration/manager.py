import threading

from django import db

from orchestra.utils.python import import_class

from . import settings
from .helpers import send_report


def as_task(execute):
    def wrapper(*args, **kwargs):
        with db.transaction.commit_manually():
            log = execute(*args, **kwargs)
            db.transaction.commit()
        if log.state != log.SUCCESS:
            send_report(execute, args, log)
        return log
    return wrapper


def close_connection(execute):
    """ Threads have their own connection pool, closing it when finishing """
    # TODO rewrite as context manager
    def wrapper(*args, **kwargs):
        log = execute(*args, **kwargs)
        db.connection.close()
        # Using the wrapper function as threader messenger for the execute output
        wrapper.log = log
    return wrapper


def execute(operations):
    """ generates and executes the operations on the servers """
    router = import_class(settings.ORCHESTRATION_ROUTER)
    # Generate scripts per server+backend
    scripts = {}
    cache = {}
    for operation in operations:
        servers = router.get_servers(operation, cache=cache)
        print cache
        for server in servers:
            key = (server, operation.backend)
            if key not in scripts:
                scripts[key] = (operation.backend(), [operation])
            else:
                scripts[key][1].append(operation)
            method = getattr(scripts[key][0], operation.action)
            method(operation.instance)
    # Execute scripts on each server
    threads = []
    executions = []
    for key, value in scripts.iteritems():
        server, __ = key
        backend, operations = value
        backend.commit()
        execute = as_task(backend.execute)
        execute = close_connection(execute)
        thread = threading.Thread(target=execute, args=(server,))
        thread.start()
        threads.append(thread)
        executions.append((execute, operations))
    [ thread.join() for thread in threads ]
    logs = []
    for execution, operations in executions:
        for operation in operations:
            operation.log = execution.log
            operation.save()
        logs.append(execution.log)
    return logs
