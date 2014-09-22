from celery import shared_task
from django.db.models.loading import get_model
from django.utils import timezone

from orchestra.apps.orchestration.models import BackendOperation as Operation

from .backends import ServiceMonitor
from .models import ResourceData, Resource


@shared_task(name='resources.Monitor')
def monitor(resource_id):
    resource = Resource.objects.get(pk=resource_id)
    
    # Execute monitors
    for monitor_name in resource.monitors:
        backend = ServiceMonitor.get_backend(monitor_name)
        model = get_model(*backend.model.split('.'))
        operations = []
        # Execute monitor
        for obj in model.objects.all():
            operations.append(Operation.create(backend, obj, Operation.MONITOR))
        Operation.execute(operations)
    
    # Update used resources and trigger resource exceeded and revovery
    operations = []
    model = resource.content_type.model_class()
    for obj in model.objects.all():
        data = ResourceData.get_or_create(obj, resource)
        data.update()
        if not resource.disable_trigger:
            if data.used < data.allocated:
                op = Operation.create(backend, obj, Operation.EXCEED)
                operations.append(op)
            elif data.used < data.allocated:
                op = Operation.create(backend, obj, Operation.RECOVERY)
                operation.append(op)
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
