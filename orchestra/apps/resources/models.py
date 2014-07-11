import datetime

from django.db import models
from django.db.models.loading import get_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from djcelery.models import PeriodicTask, CrontabSchedule

from orchestra.models.fields import MultiSelectField
from orchestra.models.utils import get_model_field_path
from orchestra.utils.apps import autodiscover

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
    
    name = models.CharField(_("name"), max_length=32, unique=True,
            help_text=_('Required. 32 characters or fewer. Lowercase letters, '
                        'digits and hyphen only.'),
            validators=[validators.RegexValidator(r'^[a-z0-9_\-]+$',
                        _('Enter a valid name.'), 'invalid')])
    verbose_name = models.CharField(_("verbose name"), max_length=256, unique=True)
    content_type = models.ForeignKey(ContentType,
            help_text=_("Model where this resource will be hooked"))
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
    is_active = models.BooleanField(_("is active"), default=True)
    disable_trigger = models.BooleanField(_("disable trigger"), default=False,
            help_text=_("Disables monitors exeeded and recovery triggers"))
    crontab = models.ForeignKey(CrontabSchedule, verbose_name=_("crontab"),
            null=True, blank=True,
            help_text=_("Crontab for periodic execution. "
                        "Leave it empty to disable periodic monitoring"))
    monitors = MultiSelectField(_("monitors"), max_length=256, blank=True,
            choices=ServiceMonitor.get_choices(),
            help_text=_("Monitor backends used for monitoring this resource."))
    
    def __unicode__(self):
        return self.name
    
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
        resource = self.resource
        today = timezone.now()
        result = 0
        has_result = False
        for monitor in resource.monitors:
            resource_model = self.content_type.model_class()
            monitor_model = get_model(ServiceMonitor.get_backend(monitor).model)
            if resource_model == monitor_model:
                dataset = MonitorData.objects.filter(monitor=monitor,
                        content_type=self.content_type_id, object_id=self.object_id)
            else:
                path = get_model_field_path(monitor_model, resource_model)
                fields = '__'.join(path)
                objects = monitor_model.objects.filter(**{fields: self.object_id})
                pks = objects.values_list('id', flat=True)
                ct = ContentType.objects.get_for_model(monitor_model)
                dataset = MonitorData.objects.filter(monitor=monitor,
                        content_type=ct, object_id__in=pks)
            if resource.period == resource.MONTHLY_AVG:
                try:
                    last = dataset.latest()
                except MonitorData.DoesNotExist:
                    continue
                has_result = True
                epoch = datetime(year=today.year, month=today.month, day=1,
                                 tzinfo=timezone.utc)
                total = (epoch-last.date).total_seconds()
                dataset = dataset.filter(date__year=today.year,
                                         date__month=today.month)
                for data in dataset:
                    slot = (previous-data.date).total_seconds()
                    result += data.value * slot/total
            elif resource.period == resource.MONTHLY_SUM:
                data = dataset.filter(date__year=today.year, date__month=today.month)
                # FIXME Aggregation of 0s returns None! django bug?
                # value = data.aggregate(models.Sum('value'))['value__sum']
                values = data.values_list('value', flat=True)
                if values:
                    has_result = True
                    result += sum(values)
            elif resource.period == resource.LAST:
                try:
                    result += dataset.latest().value
                except MonitorData.DoesNotExist:
                    continue
                has_result = True
            else:
                msg = "%s support not implemented" % self.period
                raise NotImplementedError(msg)
        return result if has_result else None


class MonitorData(models.Model):
    """ Stores monitored data """
    monitor = models.CharField(_("monitor"), max_length=256,
            choices=ServiceMonitor.get_choices())
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    value = models.PositiveIntegerField()
    
    content_object = GenericForeignKey()
    
    class Meta:
        get_latest_by = 'date'
        verbose_name_plural = _("monitor data")
    
    def __unicode__(self):
        return str(self.monitor)


def create_resource_relation():
    relation = GenericRelation('resources.ResourceData')
    for resources in Resource.group_by_content_type():
        model = resources[0].content_type.model_class()
        model.add_to_class('resources', relation)
