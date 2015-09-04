import datetime

from celery.task.schedules import crontab
from django.db import transaction
from django.utils import timezone

from orchestra.contrib.orchestration import Operation
from orchestra.contrib.tasks import task, periodic_task
from orchestra.models.utils import get_model_field_path
from orchestra.utils.sys import LockFile

from . import settings
from .backends import ServiceMonitor


@task(name='resources.Monitor')
def monitor(resource_id, ids=None):
    with LockFile('/dev/shm/resources.monitor-%i.lock' % resource_id, expire=60*60, unlocked=bool(ids)):
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
            logs += Operation.execute(monitorings, async=False)
        
        kwargs = {'id__in': ids} if ids else {}
        # Update used resources and trigger resource exceeded and revovery
        triggers = []
        model = resource.content_type.model_class()
        for obj in model.objects.filter(**kwargs):
            data, __ = ResourceData.objects.get_or_create(obj, resource)
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


@periodic_task(run_every=crontab(hour=2, minute=30), name='resources.cleanup_old_monitors')
@transaction.atomic
def cleanup_old_monitors(queryset=None):
    if queryset is None:
        from .models import MonitorData
        queryset = MonitorData.objects.all()
    delta = datetime.timedelta(days=settings.RESOURCES_OLD_MONITOR_DATA_DAYS)
    threshold = timezone.now() - delta
    queryset = queryset.filter(created_at__lt=threshold)
    delete_counts = []
    for monitor in ServiceMonitor.get_plugins():
        dataset = queryset.filter(monitor=monitor)
        delete_count = monitor.aggregate(dataset)
        delete_counts.append(
            (monitor.get_name(), delete_count)
        )
    return delete_counts
