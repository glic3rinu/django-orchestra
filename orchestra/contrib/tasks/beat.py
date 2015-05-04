import json

from celery import current_app
from celery.schedules import crontab_parser as CrontabParser
from django.utils import timezone
from djcelery.models import PeriodicTask

from .decorators import apply_async


def is_due(task, time=None):
    if time is None:
        time = timezone.now()
    crontab = task.crontab
    parts = map(int, time.strftime("%M %H %w %d %m").split())
    n_minute, n_hour, n_day_of_week, n_day_of_month, n_month_of_year = parts
    return bool(
        n_minute in CrontabParser(60).parse(crontab.minute) and
        n_hour in CrontabParser(24).parse(crontab.hour) and
        n_day_of_week in CrontabParser(7).parse(crontab.day_of_week) and
        n_day_of_month in CrontabParser(31, 1).parse(crontab.day_of_month) and
        n_month_of_year in CrontabParser(12, 1).parse(crontab.month_of_year)
    )


def run_task(task, thread=True, process=False, async=False):
    args = json.loads(task.args)
    kwargs = json.loads(task.kwargs)
    task_fn = current_app.tasks.get(task.task)
    if async:
        method = 'process' if process else 'thread'
        return apply_async(task_fn, method=method).apply_async(*args, **kwargs)
    return task_fn(*args, **kwargs)


def run():
    now = timezone.now()
    procs = []
    for task in PeriodicTask.objects.enabled().select_related('crontab'):
        if is_due(task, now):
            proc = run_task(task, process=True, async=True)
            procs.append(proc)
    [proc.join() for proc in procs]
