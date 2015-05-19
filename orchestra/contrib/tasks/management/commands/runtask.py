import json

from celery import current_app
from django.core.management.base import BaseCommand
from django.utils import timezone
from djcelery.models import PeriodicTask

from ...decorators import keep_state


class Command(BaseCommand):
    help = 'Runs Orchestra method.'
    
    def add_arguments(self, parser):
        parser.add_argument('task',
            help='Periodic task ID or task name.')
        parser.add_argument('args', nargs='*',
            help='Additional arguments passed to the task, when task name is used.')
    
    def handle(self, *args, **options):
        task = options.get('task')
        if task.isdigit():
            # periodic task
            ptask = PeriodicTask.objects.get(pk=int(task))
            task = current_app.tasks[ptask.task]
            args = json.loads(ptask.args)
            kwargs = json.loads(ptask.kwargs)
            ptask.last_run_at = timezone.now()
            ptask.total_run_count += 1
            ptask.save()
        else:
            # task name
            task = current_app.tasks[task]
            kwargs = {}
            arguments = []
            for arg in args:
                if '=' in args:
                    name, value = arg.split('=')
                    if value.isdigit():
                        value = int(value)
                    kwargs[name] = value
                else:
                    if arg.isdigit():
                        arg = int(arg)
                    arguments.append(arg)
            args = arguments
        # Run task synchronously, but logging TaskState
        keep_state(task)(*args, **kwargs)
