from celery import shared_task

from orchestra.apps.orchestration.models import BackendOperation as Operation
from orchestra.models.utils import get_model_field_path

from .backends import ServiceMonitor


@shared_task(name='resources.Monitor')
def monitor(resource_id, ids=None):
    from .models import ResourceData, Resource
    
    resource = Resource.objects.get(pk=resource_id)
    resource_model = resource.content_type.model_class()
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
        operations = []
        # Execute monitor
        for obj in model.objects.filter(**kwargs):
            operations.append(Operation.create(backend, obj, Operation.MONITOR))
        Operation.execute(operations)
    
    kwargs = {'id__in': ids} if ids else {}
    # Update used resources and trigger resource exceeded and revovery
    operations = []
    model = resource.content_type.model_class()
    for obj in model.objects.filter(**kwargs):
        data = ResourceData.get_or_create(obj, resource)
        data.update()
        if not resource.disable_trigger:
            if data.used < data.allocated:
                op = Operation.create(backend, obj, Operation.EXCEED)
                operations.append(op)
            elif data.used < data.allocated:
                op = Operation.create(backend, obj, Operation.RECOVERY)
                operations.append(op)
#        data = ResourceData.get_or_create(obj, resource)
#        current = data.get_used()
#        if not resource.disable_trigger:
#            if data.used < data.allocated and current > data.allocated:
#                op = Operation.create(backend, obj, Operation.EXCEED)
#                operations.append(op)
#            elif data.used > data.allocated and current < data.allocated:
#                op = Operation.create(backend, obj, Operation.RECOVERY)
#                operation.append(op)
#        data.update(current=current)
    Operation.execute(operations)
