from celery import shared_task
from django.utils import timezone
from orchestra.apps.orchestration.models import BackendOperation as Operation

from .backends import ServiceMonitor
from .models import MonitorData


@shared_task(name='resources.Monitor')
def monitor(resource_id):
    resource = Resource.objects.get(pk=resource_id)
    
    # Execute monitors
    for monitor_name in resource.monitors:
        backend = ServiceMonitor.get_backend(monitor_name)
        model = backend.model
        operations = []
        # Execute monitor
        for obj in model.objects.all():
            operations.append(Operation.create(backend, obj, Operation.MONITOR))
        Operation.execute(operations)
    
    # Update used resources and trigger resource exceeded and revovery
    operations = []
    model = resource.model
    for obj in model.objects.all():
        data = MonitorData.get_or_create(obj, resource)
        current = data.get_used()
        if not resource.disable_trigger:
            if data.used < data.allocated and current > data.allocated:
                op = Operation.create(backend, data.content_object, Operation.EXCEED)
                operations.append(op)
            elif res.used > res.allocated and current < res.allocated:
                op = Operation.create(backend, data.content_object, Operation.RECOVERY)
                operation.append(op)
        data.used = current
        data.las_update = timezone.now()
        data.save()
    Operation.execute(operations)
