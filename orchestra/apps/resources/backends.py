import datetime

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.functional import cached_property

from orchestra.apps.orchestration import ServiceBackend


class ServiceMonitor(ServiceBackend):
    TRAFFIC = 'traffic'
    DISK = 'disk'
    MEMORY = 'memory'
    CPU = 'cpu'
    # TODO UNITS
    
    actions = ('monitor', 'exceeded', 'recovery')
    
    @classmethod
    def get_backends(cls):
        """ filter monitor classes """
        for backend in cls.plugins:
            if backend != ServiceMonitor and ServiceMonitor in backend.__mro__:
                yield backend
    
    @cached_property
    def current_date(self):
        return timezone.now()
    
    @cached_property
    def content_type(self):
        app_label, model = self.model.split('.')
        model = model.lower()
        return ContentType.objects.get(app_label=app_label, model=model)
    
    def get_last_data(self, object_id):
        from .models import MonitorData
        try:
            return MonitorData.objects.filter(content_type=self.content_type,
                                              object_id=object_id).latest()
        except MonitorData.DoesNotExist:
            return None
        
    def get_last_date(self, object_id):
        data = self.get_last_data(object_id)
        if data is None:
            return self.current_date - datetime.timedelta(days=1)
        return data.date
    
    def process(self, line):
        """ line -> object_id, value """
        return line.split()
    
    def store(self, log):
        """ stores montirod values from stdout """
        from .models import MonitorData
        name = self.get_name()
        app_label, model_name = self.model.split('.')
        ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
        for line in log.stdout.splitlines():
            line = line.strip()
            object_id, value = self.process(line)
            MonitorData.objects.create(monitor=name, object_id=object_id,
                    content_type=ct, value=value, date=self.current_date)
    
    def execute(self, server):
        log = super(ServiceMonitor, self).execute(server)
        self.store(log)
        return log
