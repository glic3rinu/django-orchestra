from orchestra.contrib.crons.utils import apply_local

from . import settings


def celery_sync(resource, name):
    from djcelery.models import PeriodicTask
    if resource.pk and resource.crontab:
        try:
            task = PeriodicTask.objects.get(name=name)
        except PeriodicTask.DoesNotExist:
            if resource.is_active:
                PeriodicTask.objects.create(
                    name=name,
                    task='resources.Monitor',
                    args=[resource.pk],
                    crontab=resource.crontab
                )
        else:
            if task.crontab != resource.crontab:
                task.crontab = resource.crontab
                task.save(update_fields=['crontab'])
    else:
        PeriodicTask.objects.filter(
            name=name,
        ).delete()


def cron_sync(resource, name):
    if resource.pk and resource.crontab:
        context = {
            'manager': os.path.join(paths.get_project_dir(), 'manage.py'),
            'id': resource.pk,
        }
        apply_local(resource.crontab,
            'python3 %(manager)s runmethod orchestra.contrib.resources.tasks.monitor %(id)s',
            'orchestra', # TODO
            name
        )
    else:
        apply_local(resource.crontab, '', 'orchestra', name, action='delete')
