from celery.task.schedules import crontab

from orchestra.contrib.tasks import periodic_task

from .models import Service


@periodic_task(run_every=crontab(hour=5, minute=30))
def update_service_orders():
    updates = []
    for service in Service.objects.filter(periodic_update=True):
        updates += service.update_orders(commit=True)
    return updates
