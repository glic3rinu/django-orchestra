from orchestra.settings import Setting


TASKS_BACKEND = Setting('TASKS_BACKEND',
    'thread',
    choices=(
        ('thread', "threading.Thread (no queue)"),
        ('process', "multiprocess.Process (no queue)"),
        ('celery', "Celery (with queue)"),
    )
)
