from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from djcelery.models import PeriodicTask, CrontabSchedule

from orchestra.core import validators
from orchestra.models import queryset, fields

from . import helpers
from .backends import ServiceMonitor


class ResourceQuerySet(models.QuerySet):
    group_by = queryset.group_by


class Resource(models.Model):
    """
    Defines a resource, a resource is basically an interpretation of data
    gathered by a Monitor
    """
    
    LAST = 'LAST'
    MONTHLY_SUM = 'MONTHLY_SUM'
    MONTHLY_AVG = 'MONTHLY_AVG'
    PERIODS = (
        (LAST, _("Last")),
        (MONTHLY_SUM, _("Monthly Sum")),
        (MONTHLY_AVG, _("Monthly Average")),
    )
    _related = set() # keeps track of related models for resource cleanup
    
    name = models.CharField(_("name"), max_length=32,
            help_text=_('Required. 32 characters or fewer. Lowercase letters, '
                        'digits and hyphen only.'),
            validators=[validators.validate_name])
    verbose_name = models.CharField(_("verbose name"), max_length=256)
    content_type = models.ForeignKey(ContentType,
            help_text=_("Model where this resource will be hooked."))
    period = models.CharField(_("period"), max_length=16, choices=PERIODS,
            default=LAST,
            help_text=_("Operation used for aggregating this resource monitored"
                        "data."))
    on_demand = models.BooleanField(_("on demand"), default=False,
            help_text=_("If enabled the resource will not be pre-allocated, "
                        "but allocated under the application demand"))
    default_allocation = models.PositiveIntegerField(_("default allocation"),
            null=True, blank=True,
            help_text=_("Default allocation value used when this is not an "
                        "on demand resource"))
    unit = models.CharField(_("unit"), max_length=16,
            help_text=_("The unit in which this resource is measured. "
                   "For example GB, KB or subscribers"))
    scale = models.PositiveIntegerField(_("scale"),
            help_text=_("Scale in which this resource monitoring resoults should "
                        "be prorcessed to match with unit. e.g. <tt>10**9</tt>"))
    disable_trigger = models.BooleanField(_("disable trigger"), default=False,
            help_text=_("Disables monitors exeeded and recovery triggers"))
    crontab = models.ForeignKey(CrontabSchedule, verbose_name=_("crontab"),
            null=True, blank=True,
            help_text=_("Crontab for periodic execution. "
                        "Leave it empty to disable periodic monitoring"))
    monitors = fields.MultiSelectField(_("monitors"), max_length=256, blank=True,
            choices=ServiceMonitor.get_plugin_choices(),
            help_text=_("Monitor backends used for monitoring this resource."))
    is_active = models.BooleanField(_("active"), default=True)
    
    objects = ResourceQuerySet.as_manager()
    
    class Meta:
        unique_together = (
            ('name', 'content_type'),
            ('verbose_name', 'content_type')
        )
    
    def __unicode__(self):
        return "{}-{}".format(str(self.content_type), self.name)
    
    def save(self, *args, **kwargs):
        created = not self.pk
        super(Resource, self).save(*args, **kwargs)
        # Create Celery periodic task
        name = 'monitor.%s' % str(self)
        try:
            task = PeriodicTask.objects.get(name=name)
        except PeriodicTask.DoesNotExist:
            if self.is_active:
                PeriodicTask.objects.create(
                    name=name,
                    task='resources.Monitor',
                    args=[self.pk],
                    crontab=self.crontab
                )
        else:
            if not self.is_active:
                task.delete()
            elif task.crontab != self.crontab:
                task.crontab = self.crontab
                task.save(update_fields=['crontab'])
        # This only work on tests (multiprocessing used on real deployments)
        apps.get_app_config('resources').reload_relations()
        # TODO touch wsgi.py for code reloading?
    
    def delete(self, *args, **kwargs):
        super(Resource, self).delete(*args, **kwargs)
        name = 'monitor.%s' % str(self)
        PeriodicTask.objects.filter(
            name=name,
            task='resources.Monitor',
            args=[self.pk]
        ).delete()
    
    def get_scale(self):
        return eval(self.scale)


class ResourceData(models.Model):
    """ Stores computed resource usage and allocation """
    resource = models.ForeignKey(Resource, related_name='dataset', verbose_name=_("resource"))
    content_type = models.ForeignKey(ContentType, verbose_name=_("content type"))
    object_id = models.PositiveIntegerField(_("object id"))
    used = models.PositiveIntegerField(_("used"), null=True)
    updated_at = models.DateTimeField(_("updated"), null=True)
    allocated = models.PositiveIntegerField(_("allocated"), null=True, blank=True)
    
    content_object = GenericForeignKey()
    
    class Meta:
        unique_together = ('resource', 'content_type', 'object_id')
        verbose_name_plural = _("resource data")
    
    @classmethod
    def get_or_create(cls, obj, resource):
        ct = ContentType.objects.get_for_model(type(obj))
        try:
            return cls.objects.get(content_type=ct, object_id=obj.pk, resource=resource)
        except cls.DoesNotExist:
            return cls.objects.create(content_object=obj, resource=resource,
                    allocated=resource.default_allocation)
    
    @property
    def unit(self):
        return self.resource.unit
    
    def get_used(self):
        return helpers.compute_resource_usage(self)
    
    def update(self, current=None):
        if current is None:
            current = self.get_used()
        self.used = current or 0
        self.updated_at = timezone.now()
        self.save(update_fields=['used', 'updated_at'])


class MonitorData(models.Model):
    """ Stores monitored data """
    monitor = models.CharField(_("monitor"), max_length=256,
            choices=ServiceMonitor.get_plugin_choices())
    content_type = models.ForeignKey(ContentType, verbose_name=_("content type"))
    object_id = models.PositiveIntegerField(_("object id"))
    created_at = models.DateTimeField(_("created"), auto_now_add=True)
    value = models.DecimalField(_("value"), max_digits=16, decimal_places=2)
    
    content_object = GenericForeignKey()
    
    class Meta:
        get_latest_by = 'id'
        verbose_name_plural = _("monitor data")
    
    def __unicode__(self):
        return str(self.monitor)


def create_resource_relation():
    class ResourceHandler(object):
        """ account.resources.web """
        def __getattr__(self, attr):
            """ get or build ResourceData """
            try:
                data = self.obj.resource_set.get(resource__name=attr)
            except ResourceData.DoesNotExist:
                model = self.obj._meta.model_name
                resource = Resource.objects.get(content_type__model=model, name=attr,
                        is_active=True)
                data = ResourceData(content_object=self.obj, resource=resource,
                        allocated=resource.default_allocation)
            return data
        
        def __get__(self, obj, cls):
            """ proxy handled object """
            self.obj = obj
            return self
    
    # Clean previous state
    for related in Resource._related:
        try:
            delattr(related, 'resource_set')
            delattr(related, 'resources')
        except AttributeError:
            pass
        else:
            related._meta.virtual_fields = [
                field for field in related._meta.virtual_fields if field.rel.to != ResourceData
            ]
    
    relation = GenericRelation('resources.ResourceData')
    for ct, resources in Resource.objects.group_by('content_type').iteritems():
        model = ct.model_class()
        model.add_to_class('resource_set', relation)
        model.resources = ResourceHandler()
        Resource._related.add(model)
