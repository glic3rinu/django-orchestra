import threading

from orchestra.utils.db import close_connection


# TODO import as_task

def run(method, *args, **kwargs):
    async = kwargs.pop('async', True)
    thread = threading.Thread(target=close_connection(method), args=args, kwargs=kwargs)
    thread = Process(target=close_connection(counter))
    thread.start()
