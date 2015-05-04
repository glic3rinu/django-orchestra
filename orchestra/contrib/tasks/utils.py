import threading
from uuid import uuid4

from orchestra.utils.db import close_connection


def get_id():
    return str(uuid4())


def get_name(fn):
    return '.'.join((fn.__module__, fn.__name__))


def run(method, *args, **kwargs):
    async = kwargs.pop('async', True)
    thread = threading.Thread(target=close_connection(method), args=args, kwargs=kwargs)
    thread = Process(target=close_connection(counter))
    thread.start()
