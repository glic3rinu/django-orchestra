import datetime

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from orchestra.apps.orchestration import ServiceBackend
from orchestra.utils.functional import cached


class ServiceMonitor(ServiceBackend):
    TRAFFIC = 'traffic'
    DISK = 'disk'
    MEMORY = 'memory'
    CPU = 'cpu'
    
    actions = ('monitor', 'resource_exceeded', 'resource_recovery')
    
    @classmethod
    def get_backends(cls):
        """ filter monitor classes """
        for backend in cls.plugins:
            if backend != ServiceMonitor and ServiceMonitor in backend.__mro__:
                yield backend
    
    @cached
    def get_last_date(self, obj):
        from .models import MonitorData
        try:
            ct = ContentType.objects.get_for_model(type(obj))
            return MonitorData.objects.filter(content_type=ct, object_id=obj.pk).latest().date
        except MonitorData.DoesNotExist:
            return self.get_current_date() - datetime.timedelta(days=1)
    
    @cached
    def get_current_date(self):
        return timezone.now()
    
    def store(self, log):
        """ object_id value """
        from .models import MonitorData
        name = self.get_name()
        app_label, model_name = self.model.split('.')
        ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
        for line in log.stdout.splitlines():
            line = line.strip()
            object_id, value = line.split()
            MonitorData.objects.create(monitor=name, object_id=object_id,
                    content_type=ct, value=value, date=self.get_current_date())
    
    def execute(self, server):
        log = super(ServiceMonitor, self).execute(server)
        self.store(log)
        return log
