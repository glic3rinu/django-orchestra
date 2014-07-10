import datetime

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from djcelery.models import PeriodicTask, CrontabSchedule

from orchestra.models.fields import MultiSelectField
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
    content_type = models.ForeignKey(ContentType) # TODO filter by servicE?
    period = models.CharField(_("period"), max_length=16, choices=PERIODS,
            default=LAST)
    ondemand = models.BooleanField(_("on demand"), default=False)
    default_allocation = models.PositiveIntegerField(_("default allocation"),
            null=True, blank=True)
    is_active = models.BooleanField(_("is active"), default=True)
    disable_trigger = models.BooleanField(_("disable trigger"), default=False)
    crontab = models.ForeignKey(CrontabSchedule, verbose_name=_("crontab"),
            help_text=_("Crontab for periodic execution"))
    # TODO create custom field that returns backend python objects
    monitors = MultiSelectField(_("monitors"), max_length=256,
            choices=ServiceMonitor.get_choices())
    
    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super(Resource, self).save(*args, **kwargs)
        # Create Celery periodic task
        name = 'monitor.%s' % str(self)
        try:
            task = PeriodicTask.objects.get(name=name)
        except PeriodicTask.DoesNotExist:
            PeriodicTask.objects.create(name=name, task='resources.Monitor',
                                        args=[self.pk], crontab=self.crontab)
        else: 
            if task.crontab != self.crontab:
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
        for resource in cls.objects.filter(is_active=True).order_by('content_type'):
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
    allocated = models.PositiveIntegerField(null=True)
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('resource', 'content_type', 'object_id')
        verbose_name_plural = _("resource data")
    
    @classmethod
    def get_or_create(cls, obj, resource):
        try:
            return cls.objects.get(content_object=obj, resource=resource)
        except cls.DoesNotExists:
            return cls.objects.create(content_object=obj, resource=resource,
                                      allocated=resource.defalt_allocation)
    
    def get_used(self):
        resource = self.resource
        today = datetime.date.today()
        result = 0
        has_result = False
        for monitor in resource.monitors:
            dataset = MonitorData.objects.filter(monitor=monitor,
                    content_type=self.content_type, object_id=self.object_id)
            if resource.period == resource.MONTHLY_AVG:
                try:
                    last = dataset.latest()
                except MonitorData.DoesNotExist:
                    continue
                has_result = True
                epoch = datetime(year=today.year, month=today.month, day=1)
                total = (epoch-last.date).total_seconds()
                dataset = dataset.filter(date__year=today.year,
                                                 date__month=today.month)
                for data in dataset:
                    slot = (previous-data.date).total_seconds()
                    result += data.value * slot/total
            elif resource.period == resource.MONTHLY_SUM:
                data = dataset.filter(date__year=today.year,
                                      date__month=today.month)
                value = data.aggregate(models.Sum('value'))['value__sum']
                if value:
                    has_result = True
                    result += value
            elif resource.period == resource.LAST:
                try:
                    result += dataset.latest().value
                except MonitorData.DoesNotExist:
                    continue
                has_result = True
            else:
                raise NotImplementedError("%s support not implemented" % self.period)
        return result if has_result else None


class MonitorData(models.Model):
    """ Stores monitored data """
    monitor = models.CharField(_("monitor"), max_length=256,
            choices=ServiceMonitor.get_choices())
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    value = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        get_latest_by = 'date'
        verbose_name_plural = _("monitor data")
    
    def __unicode__(self):
        return str(self.monitor)


def create_resource_relation():
    relation = generic.GenericRelation('resources.ResourceData')
    for resources in Resource.group_by_content_type():
        model = resources[0].content_type.model_class()
        model.add_to_class('resources', relation)
