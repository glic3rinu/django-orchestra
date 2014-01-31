from . import collector, manager


class ProcessPendingOperations(object):
    """ processes pending backend operations """
    def process_response(self, request, response):
        operations = [ op for op  in collector.iterator() ]
        manager.execute(operations)
        return response
