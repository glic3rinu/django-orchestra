"""
    threadlocals middleware
    ~~~~~~~~~~~~~~~~~~~~~~~
    https://github.com/jedie/django-tools/blob/master/django_tools/middlewares/ThreadLocal.py
    
    MIDDLEWARE_CLASSES = (
        ...
        'orchestra.core.middlewares.ThreadLocal.ThreadLocalMiddleware',
        ...
    )
    from django_tools.middlewares import ThreadLocal
    
    # Get the current request object:
    request = ThreadLocal.get_request()
"""


from threading import local


_thread_locals = local()


def get_request():
    """ returns the request object for this thead """
    return getattr(_thread_locals, "request", None)


class ThreadLocalMiddleware(object):
    """ Simple middleware that adds the request object in thread local storage."""
    def process_request(self, request):
        _thread_locals.request = request
