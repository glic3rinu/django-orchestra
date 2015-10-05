from . import settings
from .decorators import task, periodic_task, keep_state, apply_async


default_app_config = 'orchestra.contrib.tasks.apps.TasksConfig'
