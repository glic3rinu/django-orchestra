from orchestra.contrib.settings import Setting


TASKS_BACKEND = Setting('TASKS_BACKEND',
    'thread',
    choices=(
        ('thread', "threading.Thread (no queue)"),
        ('process', "multiprocess.Process (no queue)"),
        ('celery', "Celery (with queue)"),
    )
)


TASKS_ENABLE_UWSGI_CRON_BEAT = Setting('TASKS_ENABLE_UWSGI_CRON_BEAT',
    False,
    help_text="Not implemented.",
)



TASKS_BACKEND_CLEANUP_DAYS = Setting('TASKS_BACKEND_CLEANUP_DAYS',
    10,
)
