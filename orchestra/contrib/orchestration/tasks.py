from datetime import timedelta

from celery.task.schedules import crontab
from django.utils import timezone

from orchestra.contrib.tasks import periodic_task

from . import settings
from .models import BackendLog


@periodic_task(run_every=crontab(hour=7, minute=0))
def backend_logs_cleanup():
    days = settings.ORCHESTRATION_BACKEND_CLEANUP_DAYS
    epoch = timezone.now()-timedelta(days=days)
    return BackendLog.objects.filter(created_at__lt=epoch).only('id').delete()
