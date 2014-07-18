from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djcelery.models import PeriodicTask, CrontabSchedule

from orchestra.models.fields import MultiSelectField

from . import helpers
from .backends import ServiceMonitor


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
    
    name = models.CharField(_("name"), max_length=32,
            help_text=_('Required. 32 characters or fewer. Lowercase letters, '
                        'digits and hyphen only.'),
            validators=[validators.RegexValidator(r'^[a-z0-9_\-]+$',
                        _('Enter a valid name.'), 'invalid')])
    verbose_name = models.CharField(_("verbose name"), max_length=256)
    content_type = models.ForeignKey(ContentType,
            help_text=_("Model where this resource will be hooked."))
    period = models.CharField(_("period"), max_length=16, choices=PERIODS,
            default=LAST,
            help_text=_("Operation used for aggregating this resource monitored"
                        "data."))
    ondemand = models.BooleanField(_("on demand"), default=False,
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
                        "be prorcessed to match with unit."))
    disable_trigger = models.BooleanField(_("disable trigger"), default=False,
            help_text=_("Disables monitors exeeded and recovery triggers"))
    crontab = models.ForeignKey(CrontabSchedule, verbose_name=_("crontab"),
            null=True, blank=True,
            help_text=_("Crontab for periodic execution. "
                        "Leave it empty to disable periodic monitoring"))
    monitors = MultiSelectField(_("monitors"), max_length=256, blank=True,
            choices=ServiceMonitor.get_choices(),
            help_text=_("Monitor backends used for monitoring this resource."))
    is_active = models.BooleanField(_("is active"), default=True)
    
    class Meta:
        unique_together = (
            ('name', 'content_type'),
            ('verbose_name', 'content_type')
        )
    
    def __unicode__(self):
        return "{}-{}".format(str(self.content_type), self.name)
    
    def save(self, *args, **kwargs):
        super(Resource, self).save(*args, **kwargs)
        # Create Celery periodic task
        name = 'monitor.%s' % str(self)
        try:
            task = PeriodicTask.objects.get(name=name)
        except PeriodicTask.DoesNotExist:
            if self.is_active:
                PeriodicTask.objects.create(name=name, task='resources.Monitor',
                                            args=[self.pk], crontab=self.crontab)
        else:
            if not self.is_active:
                task.delete()
            elif task.crontab != self.crontab:
                task.crontab = self.crontab
                task.save()
    
    def delete(self, *args, **kwargs):
        super(Resource, self).delete(*args, **kwargs)
        name = 'monitor.%s' % str(self)
        PeriodicTask.objects.filter(name=name, task='resources.Monitor',
                                    args=[self.pk]).delete()
    
    @classmethod
    def group_by_content_type(cls):
        prev = None
        group = []
        resources = cls.objects.filter(is_active=True).order_by('content_type')
        for resource in resources:
            ct = resource.content_type
            if prev != ct:
                if group:
                    yield group
                group = [resource]
            else:
                group.append(resource)
            prev = ct
        if group:
            yield group


class ResourceData(models.Model):
    """ Stores computed resource usage and allocation """
    resource = models.ForeignKey(Resource, related_name='dataset')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    used = models.PositiveIntegerField(null=True)
    last_update = models.DateTimeField(null=True)
    allocated = models.PositiveIntegerField(null=True, blank=True)
    
    content_object = GenericForeignKey()
    
    class Meta:
        unique_together = ('resource', 'content_type', 'object_id')
        verbose_name_plural = _("resource data")
    
    @classmethod
    def get_or_create(cls, obj, resource):
        ct = ContentType.objects.get_for_model(type(obj))
        try:
            return cls.objects.get(content_type=ct, object_id=obj.pk,
                                   resource=resource)
        except cls.DoesNotExist:
            return cls.objects.create(content_object=obj, resource=resource,
                                      allocated=resource.default_allocation)
    
    def get_used(self):
        return helpers.compute_resource_usage(self)


class MonitorData(models.Model):
    """ Stores monitored data """
    monitor = models.CharField(_("monitor"), max_length=256,
            choices=ServiceMonitor.get_choices())
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    date = models.DateTimeField(_("date"), auto_now_add=True)
    value = models.DecimalField(_("value"), max_digits=16, decimal_places=2)
    
    content_object = GenericForeignKey()
    
    class Meta:
        get_latest_by = 'date'
        verbose_name_plural = _("monitor data")
    
    def __unicode__(self):
        return str(self.monitor)


def create_resource_relation():
    class ResourceHandler(object):
        """ account.resources.web """
        def __getattr__(self, attr):
            return self.obj.resource_set.get(resource__name=attr)
        
        def __get__(self, obj, cls):
            self.obj = obj
            return self
    
    relation = GenericRelation('resources.ResourceData')
    for resources in Resource.group_by_content_type():
        model = resources[0].content_type.model_class()
        model.add_to_class('resource_set', relation)
        model.resources = ResourceHandler()
