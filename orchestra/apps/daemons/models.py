from common.collector import DependencyCollector
from common.utils.file import list_files
from common.utils.models import generate_chainer_manager
from django.db import models
from django.db.models.signals import post_save
from django.db.models.deletion import Collector
from django.dispatch import receiver
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.signals import request_started, request_finished
from django.utils.translation import ugettext as _
from django_transaction_signals import defer
from djangoplugins.fields import PluginField
from plugins import DaemonMethod
import settings
from tasks import execute


class Host(models.Model):
    ip = models.GenericIPAddressField()
    name = models.CharField(max_length=32, unique=True)
    os = models.CharField("OS", max_length=16, choices=settings.DAEMONS_OS_CHOICES, default=settings.DAEMONS_DEFAULT_OS_CHOICE)

    def __unicode__(self):
        return self.name


class DaemonQuerySet(models.query.QuerySet):

    def active(self, **kwargs):
        return self.filter(active=True, **kwargs)

    def by_object(self, obj, **kwargs):
        ct = ContentType.objects.get_for_model(obj.__class__)
        return self.filter(content_type=ct, **kwargs)
    
    
class DaemonInstance(models.Model):
    host = models.ForeignKey('daemons.Host')
    daemon = models.ForeignKey('daemons.Daemon', related_name='instances')
    expression = models.CharField(max_length=255)

    def match(self, O):
        return eval(self.expression)        
        
    def execute(self, obj, template, method, async=True, extra_context={}):
        #TODO: make it standard (return value)  
        if async: 
            # defer the execution upon successful completion of the current transaction (if exists)
            defer(execute.delay, self.pk, obj.pk, template, method, extra_context=extra_context)
        else: return execute(self.pk, obj.pk, template, method, extra_context=extra_context)


class Daemon(models.Model):
    name = models.CharField(max_length=64)
    content_type = models.ForeignKey(ContentType)
    save_method = PluginField(DaemonMethod, null=True, blank=True, related_name='daemon_save_method')
#    save_signal = models.CharField(max_length=255, choices=settings.DAEMONS_SAVE_SIGNALS, default=settings.DEFAULT_SAVE_SIGNAL)
    save_template = models.CharField(max_length=256, choices=list_files(settings.DAEMONS_TEMPLATE_PATHS), blank=True)
    delete_method = PluginField(DaemonMethod, null=True, blank=True, related_name='daemon_delete_method')
#    delete_signal = models.CharField(max_length=255, choices=settings.DELETE_SIGNALS, default=settings.DEFAULT_DELETE_SIGNAL)
    delete_template = models.CharField(max_length=256, choices=list_files(settings.DAEMONS_TEMPLATE_PATHS), blank=True)
    active = models.BooleanField(default=True)
    
    hosts = models.ManyToManyField(Host, through='DaemonInstance')
    objects = generate_chainer_manager(DaemonQuerySet)
    
    def __unicode__(self):
        return str(self.name)

    def enable(self):
        self.active = True
        self.save()
    
    def disable(self):
        self.active = False
        self.save()
    
    @classmethod
    def get_instances(cls, obj):
        if not cls.objects.filter(content_type__name=obj._meta.verbose_name_raw): 
            return []
        instances = []
        for daemon in cls.objects.active().by_object(obj):
            for instance in daemon.instances.all():
                if instance.match(obj):
                    instances.append(instance)
        return instances

    @classmethod
    def exec_save(cls, obj):
        for daemon_instance in cls.get_instances(obj):
            daemon = daemon_instance.daemon
            if daemon.save_template:
                daemon_instance.execute(obj, daemon.save_template, daemon.save_method.get_plugin())

    @classmethod
    def exec_delete(cls, obj):
        for daemon_instance in Daemon.get_instances(obj):
            daemon = daemon_instance.daemon
            if daemon.delete_template:
                daemon_instance.execute(obj, daemon.delete_template, daemon.delete_method.get_plugin())         


@receiver(post_save, sender=admin.models.LogEntry, dispatch_uid="daemon.execution_handler")
def execution_handler(sender, **kwargs):
    log_instance = kwargs['instance']
    obj = log_instance.get_edited_object()
    action = log_instance.action_flag
    dependencies = DependencyCollector(obj).objects
    #FIXME which objects will be deleted and what will be updated?
    # COllect from django delete collector
    # If bulk support do it with bulk
    if action == admin.models.DELETION:
        dependencies.pop(obj)
        collector = Collector()
        collector.collect([obj])
        Daemon.exec_delete(obj)
    for dependency in dependencies.keys():
        Daemon.exec_save(dependency)
    
    bulk_accessor.save_queue.append(obj)
        

# Bulk operation support.
# Enables bulk operation suppor for daeamons, for example on admin interface you are allowed to perform actions within a 
# set of objects. This code track down the objects envolved on this bulk operation and execute the daemon over this collection

class Bulk(object): pass
        
bulk_accessor = Bulk()

@receiver(request_started, dispatch_uid="daemon.bulk_init")
def bulk_init(sender, **kwargs):
    bulk_accessor.save_queue = []
    bulk_accessor.delete_queue = []

@receiver(request_finished, dispatch_uid="daemon.bulk_execute")
def bulk_execute(sender, **kwargs):
    if bulk_accessor.save_queue: print bulk_accessor.save_queue
    if bulk_accessor.delete_queue: print bulk_accessor.delete_queue

