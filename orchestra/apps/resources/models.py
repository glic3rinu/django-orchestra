import datetime

from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from djcelery.models import PeriodicTask, CrontabSchedule

from orchestra.utils.apps import autodiscover


class Resource(models.Model):
    MONTHLY = 'MONTHLY'
    PERIODS = (
        (MONTHLY, _('Monthly')),
    )
    
    name = models.CharField(_("name"), max_length=32, unique=True,
            help_text=_('Required. 32 characters or fewer. Lowercase letters, '
                        'digits and hyphen only.'),
            validators=[validators.RegexValidator(r'^[a-z0-9_\-]+$',
                        _('Enter a valid name.'), 'invalid')])
    verbose_name = models.CharField(_("verbose name"), max_length=256, unique=True)
    content_type = models.ForeignKey(ContentType) # TODO filter by servicE?
    period = models.CharField(_("period"), max_length=16, choices=PERIODS,
            default=MONTHLY)
    ondemand = models.BooleanField(default=False)
    default_allocation = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    disable_trigger = models.BooleanField(default=False)
    
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
        for monitor in self.monitors.all():
            has_result = True
            if self.period == self.MONTHLY:
                data = monitor.dataset.filter(date__year=today.year,
                                              date__month=today.month)
                result += data.aggregate(models.Sum('value'))['value__sum']
            else:
                raise NotImplementedError("%s support not implemented" % self.period)
        return result if has_result else None


class ResourceAllocation(models.Model):
    resource = models.ForeignKey(Resource)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    value = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey()
    
    class Meta:
        unique_together = ('resource', 'content_type', 'object_id')


autodiscover('monitors')


class Monitor(models.Model):
    backend = models.CharField(_("backend"), max_length=256,)
#            choices=MonitorBackend.get_choices())
    resource = models.ForeignKey(Resource, related_name='monitors')
    crontab = models.ForeignKey(CrontabSchedule)
    
    class Meta:
        unique_together=('backend', 'resource')
    
    def __unicode__(self):
        return self.backend


class MonitorData(models.Model):
    monitor = models.ForeignKey(Monitor, related_name='dataset')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    value = models.PositiveIntegerField()
    
    content_object = generic.GenericForeignKey()
    
    def __unicode__(self):
        return str(self.monitor)
