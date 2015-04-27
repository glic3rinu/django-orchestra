from datetime import timedelta

from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.utils import timezone

from .models import BackendLog


@periodic_task(run_every=crontab(hour=7, minute=30, day_of_week=1))
def backend_logs_cleanup(run_every=run_every):
    days = settings.ORCHESTRATION_BACKEND_CLEANUP_DAYS
    epoch = timezone.now()-timedelta(days=days)
    BackendLog.objects.filter(created_at__lt=epoch).delete()
