from celery import registry
from common.utils.file import list_files
from common.utils.models import generate_chainer_manager, group_by
from daemons import settings as daemon_settings
from daemons.models import Daemon
from daemons.plugins import DaemonMethod
from datetime import datetime
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _
from djangoplugins.fields import PluginField 
from djcelery.models import PeriodicTask, IntervalSchedule, CrontabSchedule 
from helpers import split_period
from resources import settings


class MonitorQuerySet(models.query.QuerySet):
    """Manager for Version models."""
    def by_object(self, obj, **kwargs):
        ct = ContentType.objects.get_for_model(obj)
        return self.filter(daemon__content_type=ct, **kwargs)
        
    def active(self, **kwargs):
        return self.filter(active=True, **kwargs)

class Monitor(models.Model):
    daemon = models.ForeignKey(Daemon, help_text=_('Used for find the object: content_type + Host + expression'))
    resource = models.CharField(max_length=32, choices=settings.RESOURCES_RESOURCE_CHOICES)
    monitoring_template = models.CharField(max_length=256, choices=list_files(settings.RESOURCES_TEMPLATE_PATHS))
    monitoring_method = PluginField(DaemonMethod, null=True, blank=True, related_name='monitoring_method')
    exceed_trigger_template = models.CharField(max_length=256, blank=True, choices=list_files(settings.RESOURCES_TEMPLATE_PATHS))
    exceed_trigger_method = PluginField(DaemonMethod, null=True, blank=True, related_name='exceed_trigger_method')
    recover_trigger_template = models.CharField(max_length=256, blank=True, choices=list_files(settings.RESOURCES_TEMPLATE_PATHS))
    recover_trigger_method = PluginField(DaemonMethod, null=True, blank=True, related_name='recover_trigger_method')
    allow_limit = models.BooleanField(default=True, help_text=_("This monitor *can* be limited"))
    allow_unlimit = models.BooleanField(default=True, help_text=_("This monitor *can* have unlimited resources"))
    default_initial = models.IntegerField(default=0, help_text=_("0 means unlimited, x>0 means limited"))
    block_size = models.IntegerField(default=1)
    algorithm = models.CharField(max_length=4, choices=settings.RESOURCES_ALGORITHM_CHOICES, default=settings.RESOURCES_ALGORITHM_DEFAULT)
    period = models.CharField(max_length=1, choices=settings.RESOURCES_PERIOD_CHOICES, blank=True)
    
    interval = models.ForeignKey(IntervalSchedule, null=True, blank=True)
    crontab = models.ForeignKey(CrontabSchedule, null=True, blank=True, help_text=_(u"Use one of interval/crontab"))
    active = models.BooleanField(default=True)
    
    objects = generate_chainer_manager(MonitorQuerySet)
    
    class Meta:
        unique_together=('daemon', 'resource')

    def __unicode__(self):
        return "%s[%s]" % (self.daemon, self.resource)

    def save(self, *args, **kwargs):
        super(Monitor, self).save(*args, **kwargs)
        # Create Celery periodic task
        name = str(self)
        try: existing = PeriodicTask.objects.get(name=name)
        except PeriodicTask.DoesNotExist:
            if self.interval: schedule = {'interval': self.interval}
            else: schedule = {'crontab': self.crontab}
            PeriodicTask.objects.create(name=name, task='Monitoring', args=[self.pk], **schedule)
        else: 
            if existing.crontab != self.crontab: 
                existing.crontab = self.crontab
                existing.save()
            elif existing.interval != self.interval: 
                existing.interval = self.interval
                existing.save()
            
    def delete(self, *args, **kwargs):
        # Delete Celery related periodic task
        try: PeriodicTask.objects.get(name=str(self), task='Monitoring', args=[self.pk]).delete()
        except PeriodicTask.DoesNotExist: pass
        super(Monitor, self).delete(*args, **kwargs)

    @property
    def content_type(self):
        return self.daemon.content_type

    @property
    def has_partners(self):
        if self.__class__.objects.filter(daemon__content_type=self.content_type, active=True): 
            return True
        else: 
            return False

    def record(self, obj, data, date=None):
        if not date: date = datetime.now()
        Monitoring.store_monitorization_result(self, obj, data, date)
            
    def has_different_configuration(self, mon):
        if self.allow_limit != mon.allow_limit: return True
        if self.allow_unlimit != mon.allow_unlimit: return True
        if self.block_size != mon.block_size: return True
        if self.algorithm != mon.algorithm: return True
        if self.period != mon.period: return True
        if self.default_initial != mon.default_initial: return True
        return False

    @classmethod
    def get_grouped(cls):
        #TODO: convert to Manager
        monitors = cls.objects.active().order_by('daemon__content_type')
        #return group_by_content_type(monitors)
        return group_by(cls, 'daemon__content_type', monitors, queryset=False)
 
    @classmethod
    def get_monitor(cls, obj, resource):
        #TODO: multidaemon support
        daemon = Daemon.get_instances(obj)[0]
        return cls.objects.get(daemon=daemon, resource=resource)

    def disable(self):
        self.active = False
        self.save()
        
    def enable(self):
        self.active = True
        self.save()


class MonitoringQuerySet(models.query.QuerySet):
    """Manager for Version models."""
    def last(self, obj, monitor):
        """ return active orders """
        ct = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=ct, object_id=obj.pk, monitor=monitor)[0]
        #except IndexError: return None

    def get_last(self, **kwargs):
        try: return self.filter(**kwargs).order_by('-date')[0]
        except IndexError: raise Monitoring.DoesNotExist

    def by_object(self, obj, **kwargs):
        ct = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=ct, object_id=obj.pk).filter(**kwargs)

    def last_of_this_type(self, monitoring):
        """ return active orders """
        return self.filter(content_type=monitoring.content_type, object_id=monitoring.object_id, monitor=monitoring.monitor)[0]

#TODO move to common.models


#from common.models import BasePlugin, plugin_auto_updated
class Monitoring(models.Model):
    monitor = models.ForeignKey(Monitor)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    limit = models.BigIntegerField(null=True, blank=True)
    current = models.BigIntegerField(null=True, blank=True)
    last = models.BigIntegerField(null=True, blank=True)
    date = models.DateTimeField()
    
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = generate_chainer_manager(MonitoringQuerySet)

    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        return "%s of %s" % (self.monitor.resource, self.content_object)

    @property
    def resource(self):
        return self.monitor.resource
    
    @classmethod
    def get_limit(cls, obj, monitor):
        try: last = Monitoring.objects.by_object(obj, monitor=monitor).get_last()
        except Monitoring.DoesNotExist: return monitor.default_initial
        else: return last.limit 
        
    
    @classmethod
    def get_current(cls, obj, monitor):
        try: return cls.objects.last(obj=obj, monitor=monitor).current        
        except IndexError: return None
        
    @classmethod
    def calculate_current(cls, self):
        if not self.last:
            qset = cls.objects.by_object(obj=self.content_object, monitor=self.monitor).order_by('-date')
            count = qset.count() 
            if count > 0 and qset[0].current: return qset[0].current
            elif count > 1: return qset[1].current
            else: return None
                    
        algorithm = self.monitor.algorithm
        if algorithm == 'Last':
            return self.last
        else:
            exec "from django.db.models import %s as operation" % algorithm
            #TODO use __import__
            ini, fi = split_period(self.monitor.period)
            used = Monitoring.objects.by_object(self.content_object, date__gte=ini, date__lte=fi).aggregate(operation('last')).values()[0]
            try: used_blocks = used / self.monitor.block_size
            except TypeError: 
                if self.current: return self.current
                else: return self.last
            if used % self.monitor.block_size: used_blocks += 1
            used = used_blocks * self.monitor.block_size
            return used
            # used if used > self.current else self.current

    @classmethod
    def store_monitorization_result(cls, monitor, obj, value, date):
        """ save Monitor execution """ 
        cls(monitor = monitor,
            content_type = monitor.content_type,
            object_id = obj.pk,
            limit = cls.get_limit(obj, monitor),
            last = value,
            date = date).save()

    def save(self, *args, **kwargs):
        # Generate current value
        # Hack: if we pass cls kwarg to save_base then signals are not trigged :)
        super(Monitoring, self).save_base(*args, cls=Monitoring, **kwargs)
        self.current = Monitoring.calculate_current(self)
        super(Monitoring, self).save(*args, **kwargs)

    @property
    def service_instance(self):
        return self.content_object



def last_monitorization(self, monitor):
    """ monitor could be a Monitor or a resource str """
    if isinstance(monitor, str):
        monitor = Monitor.objects.get(daemon=Daemon.objects.by_object(self), resource=monitor)
    try: last = Monitoring.objects.by_object(self, monitor=monitor).get_last()
    except Monitoring.DoesNotExist: last = None
    return last


#TODO: use this on forms
def get_limit(self, monitor):
    return Monitoring.get_limit(self, monitor)


def monitoring_register(monitors):
    """ Register this resource extention to models, and add reverse relation"""
    # maybe there is a better way to do that. But it must be after monitor table creation.
    from django.db import connection
    cursor = connection.cursor()
    if 'resources_monitor' in connection.introspection.get_table_list(cursor):
        for ct_pk in monitors.values_list('daemon__content_type', flat=True).distinct():
            model = ContentType.objects.get(pk=ct_pk).model_class()
            generic.GenericRelation('resources.Monitoring').contribute_to_class(model, 'monitoring')
            model.last_monitorization = last_monitorization
            model.get_limit = get_limit

monitoring_register(Monitor.objects.filter(active=True))
