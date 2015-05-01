from orchestra.settings import Setting


RESOURCES_TASK_BACKEND = Setting('RESOURCES_TASK_BACKEND',
    'orchestra.contrib.resources.utils.cron_sync'
)
