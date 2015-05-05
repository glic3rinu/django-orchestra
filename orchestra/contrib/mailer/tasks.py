from django.utils import timezone
from celery.task.schedules import crontab

from orchestra.contrib.tasks import task, periodic_task

from . import engine


@task
def send_message(message):
    engine.send_message(message)


@periodic_task(run_every=crontab(hour=7, minute=30))
def cleanup_messages():
    from .models import Message
    delta = timedelta(days=settings.MAILER_MESSAGES_CLEANUP_DAYS)
    now = timezone.now()
    epoch = (now-delta)
    Message.objects.filter(state=Message.SENT, last_retry__lt=epoc).delete()
