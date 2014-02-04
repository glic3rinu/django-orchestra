from threading import local


class OperationsMiddleware(object):
    _thread_locals = local()
    
    @classmethod
    def get_request(cls):
        """ returns the request object for this thead """
        return getattr(cls._thread_locals, "request", None)
    
    def process_request(self, request):
        """ store request on a thread local variable """
        type(self)._thread_locals.request = request
    
    def process_response(self, request, response):
        """ processes pending backend operations """
        from . import collector, manager
        operations = [ op for op  in collector.iterator() ]
        manager.execute(operations)
        return response
