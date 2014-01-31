from . import settings


def get_router():
    module = '.'.join(settings.ORCHESTRATION_ROUTER.split('.')[:-1])
    cls = settings.ORCHESTRATION_ROUTER.split('.')[-1]
    module = __import__(module, fromlist=[module])
    return getattr(module, cls)


def execute(operations):
    """ generates and executes the operations on remote servers """
    router = get_router()
    # Generate scripts per server+backend
    scripts = {}
    for operation in operations:
        servers = router.get_servers(operation)
        for server in servers:
            key = (server, operation.backend)
            if key not in scripts:
                scripts[key] = operation.backend()
            getattr(scripts[key], operation.action)(operation.obj)
    # Execute scripts on each server
    for key, backend in scripts.iteritems():
        server, __ = key
        backend.commit()
        backend.execute(server)
