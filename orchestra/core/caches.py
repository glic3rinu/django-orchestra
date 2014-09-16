from threading import currentThread

from django.core.cache.backends.dummy import DummyCache
from django.core.cache.backends.locmem import LocMemCache


_request_cache = {}


class RequestCache(LocMemCache):
    """ LocMemCache is a threadsafe local memory cache """
    def __init__(self):
        name = 'locmemcache@%i' % hash(currentThread())
        super(RequestCache, self).__init__(name, {})


def get_request_cache():
    """
    Returns per-request cache when running RequestCacheMiddleware otherwise a
    DummyCache instance (when running periodic tasks, tests or shell)
    """
    try:
        return _request_cache[currentThread()]
    except KeyError:
        return DummyCache('dummy', {})


class RequestCacheMiddleware(object):
    def process_request(self, request):
        cache = _request_cache.get(currentThread(), RequestCache())
        _request_cache[currentThread()] = cache
        cache.clear()
    
    def process_response(self, request, response):
        if currentThread() in _request_cache:
            _request_cache[currentThread()].clear()
        return response
