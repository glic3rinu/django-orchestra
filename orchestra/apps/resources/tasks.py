from celery import shared_task

from .backends import ServiceMonitor


@shared_task
def monitor(backend_name):
    routes = Route.objects.filter(is_active=True, backend=backend_name)
    for route in routes:
        pass
    for backend in ServiceMonitor.get_backends():
        if backend.get_name() == backend_name:
    # TODO execute monitor BackendOperation
           pass
