from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

from orchestra.core import administration


class TasksConfig(AppConfig):
    name = 'orchestra.contrib.tasks'
    verbose_name = "Tasks"
    
    def ready(self):
        from djcelery.models import PeriodicTask, TaskState, WorkerState
        administration.register(TaskState, icon='Edit-check-sheet.png')
        administration.register(PeriodicTask, parent=TaskState, icon='Appointment.png')
        administration.register(WorkerState, parent=TaskState, dashboard=False)
        autodiscover_modules('tasks')
