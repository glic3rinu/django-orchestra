import datetime

from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.orchestration import ServiceBackend

from . import helpers


class ServiceMonitor(ServiceBackend):
    TRAFFIC = 'traffic'
    DISK = 'disk'
    MEMORY = 'memory'
    CPU = 'cpu'
    # TODO UNITS
    actions = ('monitor', 'exceeded', 'recovery')
    abstract = True
    delete_old_equal_values = False
    monthly_sum_old_values = False
    
    @classmethod
    def get_plugins(cls):
        """ filter controller classes """
        return [
            plugin for plugin in cls.plugins if issubclass(plugin, ServiceMonitor)
        ]
    
    @classmethod
    def get_verbose_name(cls):
        return _("[M] %s") % super(ServiceMonitor, cls).get_verbose_name()
    
    @cached_property
    def current_date(self):
        return timezone.now()
    
    @cached_property
    def content_type(self):
        from django.contrib.contenttypes.models import ContentType
        app_label, model = self.model.split('.')
        model = model.lower()
        return ContentType.objects.get_by_natural_key(app_label, model)
    
    def get_last_data(self, object_id):
        from .models import MonitorData
        try:
            return MonitorData.objects.filter(content_type=self.content_type,
                monitor=self.get_name(), object_id=object_id).latest()
        except MonitorData.DoesNotExist:
            return None
        
    def get_last_date(self, object_id):
        data = self.get_last_data(object_id)
        if data is None:
            return self.current_date - datetime.timedelta(days=1)
        return data.created_at
    
    def process(self, line):
        """ line -> object_id, value, state"""
        result = line.split()
        if len(result) != 2:
            cls_name = self.__class__.__name__
            raise ValueError("%s expected '<id> <value>' got '%s'" % (cls_name, line))
        # State is None, unless your monitor needs to keep track of it
        result.append(None)
        return result
    
    def store(self, log):
        """ stores monitored values from stdout """
        from django.contrib.contenttypes.models import ContentType
        from .models import MonitorData
        name = self.get_name()
        app_label, model_name = self.model.split('.')
        ct = ContentType.objects.get_by_natural_key(app_label, model_name.lower())
        for line in log.stdout.splitlines():
            line = line.strip()
            object_id, value, state = self.process(line)
            if isinstance(value, bytes):
                value = value.decode('ascii')
            if isinstance(state, bytes):
                state = state.decode('ascii')
            content_object = ct.get_object_for_this_type(pk=object_id)
            MonitorData.objects.create(
                monitor=name, object_id=object_id, content_type=ct, value=value, state=state,
                created_at=self.current_date, content_object_repr=str(content_object),
            )
    
    def execute(self, *args, **kwargs):
        log = super(ServiceMonitor, self).execute(*args, **kwargs)
        self.store(log)
        return log
    
    @classmethod
    def aggregate(cls, dataset):
        if cls.delete_old_equal_values:
            return helpers.delete_old_equal_values(dataset)
        elif cls.monthly_sum_old_values:
            return helpers.monthly_sum_old_values(dataset)
