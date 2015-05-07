This is a wrapper around djcelery and celery `@task` and `@periodic_task` decorators. It provides transparent support for switching between executing a task on a plain Python thread or
pushing the task on a queue (rabbitmq) and executing it on a Celery worker.

A queueless threaded execution has the advantage of 0 moving parts instead of the alternative rabbitmq and celery workers. Less dependencies, less memory footprint, less points of failure.

If your application needs to run thousands or milions of tasks a day, use celery as your backend, if tens or hundreds, then probably the default thread backend will be your best choice.
