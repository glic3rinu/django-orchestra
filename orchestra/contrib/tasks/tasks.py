from datetime import timedelta

from celery.task.schedules import crontab
from django.utils import timezone
from djcelery.models import TaskState

from . import periodic_task, settings


@periodic_task(run_every=crontab(hour=6, minute=0))
def backend_logs_cleanup():
    days = settings.TASKS_BACKEND_CLEANUP_DAYS
    epoch = timezone.now()-timedelta(days=days)
    return TaskState.objects.filter(tstamp__lt=epoch).only('id').delete()
