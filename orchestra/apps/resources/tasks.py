from celery.task import task
from datetime import datetime
from django.db import transaction


@task(name="Monitoring")
def execute_monitor(monitor_pk):
    from daemons.models import Daemon
    from resources.models import Monitor
    monitor = Monitor.objects.get(pk=monitor_pk, active=True)
    for obj in monitor.content_type.model_class().objects.all():
        for daemon_instance in Daemon.get_instances(obj):
            with transaction.commit_on_success(): 
                now = datetime.now()
                last = obj.last_monitorization(monitor)
                last = last.date if last else now
                result = daemon_instance.execute(obj,
                                        monitor.monitoring_template, 
                                        monitor.monitoring_method.get_plugin(), 
                                        extra_context={'start_date': last,
                                                       'end_date': now,
                                                       'monitor': monitor},
                                                        async = False)
                monitor.record(obj=obj, date=now, data=result[0])

