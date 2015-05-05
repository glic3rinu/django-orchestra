import traceback
from functools import partial, wraps, update_wrapper
from multiprocessing import Process
from threading import Thread

from celery import shared_task as celery_shared_task
from celery import states
from celery.decorators import periodic_task as celery_periodic_task
from django.utils import timezone

from orchestra.utils.db import close_connection
from orchestra.utils.python import AttrDict, OrderedSet

from .utils import get_name, get_id


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
        thread = method(target=fn, args=args, kwargs=kwargs)
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
        raise NotImplementedError("%s concurrency method is not supported." % method)
    fn.apply_async = partial(inner, close_connection(keep_state(fn)), name, method)
    fn.delay = fn.apply_async
    return fn


def task(fn=None, **kwargs):
    # TODO override this if 'celerybeat' in sys.argv ?
    from . import settings
    # register task
    if fn is None:
        name = kwargs.get('name', None)
        if settings.TASKS_BACKEND in ('thread', 'process'):
            def decorator(fn):
                return apply_async(celery_shared_task(**kwargs)(fn), name=name)
            return decorator
        else:
            return celery_shared_task(**kwargs)
    fn = celery_shared_task(fn)
    if settings.TASKS_BACKEND in ('thread', 'process'):
        fn = apply_async(fn)
    return fn


def periodic_task(fn=None, **kwargs):
    from . import settings
    # register task
    if fn is None:
        name = kwargs.get('name', None)
        if settings.TASKS_BACKEND in ('thread', 'process'):
            def decorator(fn):
                return apply_async(celery_periodic_task(**kwargs)(fn), name=name)
            return decorator
        else:
            return celery_periodic_task(**kwargs)
    fn = celery_periodic_task(fn)
    if settings.TASKS_BACKEND in ('thread', 'process'):
        name = kwargs.pop('name', None)
        fn = update_wrapper(apply_async(fn, name), fn)
    return fn
