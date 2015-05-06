from orchestra.contrib.orchestration import Operation
from orchestra.contrib.tasks import task
from orchestra.models.utils import get_model_field_path
from orchestra.utils.sys import LockFile

from .backends import ServiceMonitor


@task(name='resources.Monitor')
def monitor(resource_id, ids=None, async=True):
    with LockFile('/dev/shm/resources.monitor-%i.lock' % resource_id, expire=60*60):
        from .models import ResourceData, Resource
        resource = Resource.objects.get(pk=resource_id)
        resource_model = resource.content_type.model_class()
        logs = []
        # Execute monitors
        for monitor_name in resource.monitors:
            backend = ServiceMonitor.get_backend(monitor_name)
            model = backend.model_class()
            kwargs = {}
            if ids:
                path = get_model_field_path(model, resource_model)
                path = '%s__in' % ('__'.join(path) or 'id')
                kwargs = {
                    path: ids
                }
            # Execute monitor
            monitorings = []
            for obj in model.objects.filter(**kwargs):
                op = Operation(backend, obj, Operation.MONITOR)
                monitorings.append(op)
            # TODO async=True only when running with celery
            # monitor.request.id
            logs += Operation.execute(monitorings, async=async)
        
        kwargs = {'id__in': ids} if ids else {}
        # Update used resources and trigger resource exceeded and revovery
        triggers = []
        model = resource.content_type.model_class()
        for obj in model.objects.filter(**kwargs):
            data, __ = ResourceData.get_or_create(obj, resource)
            data.update()
            if not resource.disable_trigger:
                a = data.used
                b = data.allocated
                if data.used > (data.allocated or 0):
                    op = Operation(backend, obj, Operation.EXCEEDED)
                    triggers.append(op)
                elif data.used < (data.allocated or 0):
                    op = Operation(backend, obj, Operation.RECOVERY)
                    triggers.append(op)
        Operation.execute(triggers)
        return logs
