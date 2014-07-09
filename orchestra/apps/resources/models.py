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
    monitors = MultiSelectField(_("monitors"), max_length=256,
            choices=ServiceMonitor.get_choices())
    
    def __unicode__(self):
        return self.name
    
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
    
    def get_current(self):
        today = datetime.date.today()
        result = 0
        has_result = False
        for monitor in self.monitors:
            dataset = MonitorData.objects.filter(monitor=monitor)
            if self.period == self.MONTHLY_AVG:
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
            elif self.period == self.MONTHLY_SUM:
                data = dataset.filter(date__year=today.year,
                                      date__month=today.month)
                value = data.aggregate(models.Sum('value'))['value__sum']
                if value:
                    has_result = True
                    result += value
            elif self.period == self.LAST:
                try:
                    result += dataset.latest().value
                except MonitorData.DoesNotExist:
                    continue
                has_result = True
            else:
                raise NotImplementedError("%s support not implemented" % self.period)
        return result if has_result else None


class ResourceData(models.Model):
    """ Stores computed resource usage and allocation """
    resource = models.ForeignKey(Resource)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    used = models.PositiveIntegerField(null=True)
    last_update = models.DateTimeField(null=True)
    allocated = models.PositiveIntegerField(null=True)
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('resource', 'content_type', 'object_id')
        verbose_name_plural = _("resource data")

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
