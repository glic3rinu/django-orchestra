import traceback
from functools import partial, wraps, update_wrapper
from multiprocessing import Process
from uuid import uuid4
from threading import Thread

from celery import shared_task as celery_shared_task
from celery import states
from celery.decorators import periodic_task as celery_periodic_task
from django.utils import timezone

from orchestra.utils.db import close_connection
from orchestra.utils.python import AttrDict, OrderedSet


def get_id():
    return str(uuid4())


def get_name(fn):
    return '.'.join((fn.__module__, fn.__name__))


def keep_state(fn):
    """ logs task on djcelery's TaskState model """
    @wraps(fn)
    def wrapper(task_id, name, *args, **kwargs):
        from djcelery.models import TaskState
        now = timezone.now()
        state = TaskState.objects.create(state=states.STARTED, task_id=task_id, name=name, args=str(args),
            kwargs=str(kwargs), tstamp=now)
        try:
            result = fn(*args, **kwargs)
        except Exception as exc:
            state.state = states.FAILURE
            state.traceback = traceback.format_exc()
            state.runtime = (timezone.now()-now).total_seconds()
            state.save()
            return
            # TODO send email
        else:
            state.state = states.SUCCESS
            state.result = str(result)
            state.runtime = (timezone.now()-now).total_seconds()
            state.save()
        return result
    return wrapper


def apply_async(fn, name=None, method='thread'):
    """ replaces celery apply_async """
    def inner(fn, name, method, *args, **kwargs):
        task_id = get_id()
        args = (task_id, name) + args
        thread = Process(target=fn, args=args, kwargs=kwargs)
        thread.start()
        # Celery API compat
        thread.request = AttrDict(id=task_id)
        return thread
    if name is None:
        name = get_name(fn)
    if method == 'thread':
        method = Thread
    elif method == 'process':
        method = Process
    else:
        raise NotImplementedError("Support for %s concurrency method is not supported." % method)
    fn.apply_async = partial(inner, close_connection(keep_state(fn)), name, method)
    return fn


def apply_async_override(fn, name):
    if fn is None:
        def decorator(fn):
            return update_wrapper(apply_async(fn), fn)
        return decorator
    return update_wrapper(apply_async(fn, name), fn)


def task(fn=None, **kwargs):
    # TODO override this if 'celerybeat' in sys.argv ?
    from . import settings
    # register task
    if fn is None:
        fn = celery_shared_task(**kwargs)
    else:
        fn = celery_shared_task(fn)
    if settings.TASKS_BACKEND in ('thread', 'process'):
        name = kwargs.pop('name', None)
        apply_async_override(fn, name)
    return fn


def periodic_task(fn=None, **kwargs):
    from . import settings
    # register task
    if fn is None:
        fn = celery_periodic_task(**kwargs)
    else:
        fn = celery_periodic_task(fn)
    if settings.TASKS_BACKEND in ('thread', 'process'):
        name = kwargs.pop('name', None)
        apply_async_override(fn, name)
    return fn
