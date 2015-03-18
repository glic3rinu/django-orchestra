from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.db import models
from django.db.models.loading import get_model
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from djcelery.models import PeriodicTask, CrontabSchedule

from orchestra.core import validators
from orchestra.models import queryset, fields
from orchestra.models.utils import get_model_field_path
from orchestra.utils.paths import get_project_root
from orchestra.utils.system import run

from . import helpers, tasks
from .backends import ServiceMonitor
from .validators import validate_scale


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
            help_text=_("Required. 32 characters or fewer. Lowercase letters, "
                        "digits and hyphen only."),
            validators=[validators.validate_name])
    verbose_name = models.CharField(_("verbose name"), max_length=256)
    content_type = models.ForeignKey(ContentType,
            help_text=_("Model where this resource will be hooked."))
    period = models.CharField(_("period"), max_length=16, choices=PERIODS,
            default=LAST,
            help_text=_("Operation used for aggregating this resource monitored data."))
    on_demand = models.BooleanField(_("on demand"), default=False,
            help_text=_("If enabled the resource will not be pre-allocated, "
                        "but allocated under the application demand"))
    default_allocation = models.PositiveIntegerField(_("default allocation"),
            null=True, blank=True,
            help_text=_("Default allocation value used when this is not an "
                        "on demand resource"))
    unit = models.CharField(_("unit"), max_length=16,
            help_text=_("The unit in which this resource is represented. "
                        "For example GB, KB or subscribers"))
    scale = models.CharField(_("scale"), max_length=32, validators=[validate_scale],
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
    
    def clean(self):
        self.verbose_name = self.verbose_name.strip()
        # Validate that model path exists between ct and each monitor.model
        monitor_errors = []
        for monitor in self.monitors:
            try:
                self.get_model_path(monitor)
            except (RuntimeError, LookupError):
                model = get_model(ServiceMonitor.get_backend(monitor).model)
                monitor_errors.append(model._meta.model_name)
        if monitor_errors:
            model_name = self.content_type.model_class()._meta.model_name
            raise validators.ValidationError({
                'monitors': [
                    _("Path does not exists between '%s' and '%s'") % (
                        error,
                        model_name,
                    ) for error in monitor_errors
                ]})
    
    def save(self, *args, **kwargs):
        created = not self.pk
        super(Resource, self).save(*args, **kwargs)
        self.sync_periodic_task()
        # This only work on tests (multiprocessing used on real deployments)
        apps.get_app_config('resources').reload_relations()
        run('sleep 2 && touch %s/wsgi.py' % get_project_root(), async=True)
    
    def delete(self, *args, **kwargs):
        super(Resource, self).delete(*args, **kwargs)
        name = 'monitor.%s' % str(self)
    
    def get_model_path(self, monitor):
        """ returns a model path between self.content_type and monitor.model """
        resource_model = self.content_type.model_class()
        monitor_model = ServiceMonitor.get_backend(monitor).model_class()
        return get_model_field_path(monitor_model, resource_model)
    
    def sync_periodic_task(self):
        name = 'monitor.%s' % str(self)
        if self.pk and self.crontab:
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
                if task.crontab != self.crontab:
                    task.crontab = self.crontab
                    task.save(update_fields=['crontab'])
        else:
            PeriodicTask.objects.filter(
                name=name,
            ).delete()
    
    def get_scale(self):
        return eval(self.scale)
    
    def get_verbose_name(self):
        return self.verbose_name or self.name
    
    def monitor(self, async=True):
        if async:
            return tasks.monitor.delay(self.pk, async=async)
        return tasks.monitor(self.pk, async=async)


class ResourceData(models.Model):
    """ Stores computed resource usage and allocation """
    resource = models.ForeignKey(Resource, related_name='dataset', verbose_name=_("resource"))
    content_type = models.ForeignKey(ContentType, verbose_name=_("content type"))
    object_id = models.PositiveIntegerField(_("object id"))
    used = models.DecimalField(_("used"), max_digits=16, decimal_places=3, null=True,
            editable=False)
    updated_at = models.DateTimeField(_("updated"), null=True, editable=False)
    allocated = models.DecimalField(_("allocated"), max_digits=8, decimal_places=2,
            null=True, blank=True)
    content_object = GenericForeignKey()
    
    class Meta:
        unique_together = ('resource', 'content_type', 'object_id')
        verbose_name_plural = _("resource data")
    
    @classmethod
    def get_or_create(cls, obj, resource):
        ct = ContentType.objects.get_for_model(type(obj))
        try:
            return cls.objects.get(
                content_type=ct,
                object_id=obj.pk,
                resource=resource
            )
        except cls.DoesNotExist:
            return cls.objects.create(
                content_object=obj,
                resource=resource,
                allocated=resource.default_allocation
            )
    
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
    
    def monitor(self, async=False):
        ids = (self.object_id,)
        if async:
            return tasks.monitor.delay(self.resource_id, ids=ids, async=async)
        return tasks.monitor(self.resource_id, ids=ids, async=async)
    
    def get_monitor_datasets(self):
        resource = self.resource
        today = timezone.now()
        datasets = []
        for monitor in resource.monitors:
            path = self.resource.get_model_path(monitor)
            if path == []:
                dataset = MonitorData.objects.filter(
                    monitor=monitor,
                    content_type=self.content_type_id,
                    object_id=self.object_id
                )
            else:
                fields = '__'.join(path)
                monitor_model = ServiceMonitor.get_backend(monitor).model_class()
                objects = monitor_model.objects.filter(**{fields: self.object_id})
                pks = objects.values_list('id', flat=True)
                ct = ContentType.objects.get_for_model(monitor_model)
                dataset = MonitorData.objects.filter(
                    monitor=monitor,
                    content_type=ct,
                    object_id__in=pks
                )
            if resource.period in (resource.MONTHLY_AVG, resource.MONTHLY_SUM):
                datasets.append(
                    dataset.filter(
                        created_at__year=today.year,
                        created_at__month=today.month
                    )
                )
            elif resource.period == resource.LAST:
                # Get last monitoring data per object_id
                try:
                    datasets.append(
                        dataset.order_by('object_id', '-id').distinct('object_id')
                    )
                except MonitorData.DoesNotExist:
                    continue
            else:
                raise NotImplementedError("%s support not implemented" % self.period)
        return datasets


class MonitorData(models.Model):
    """ Stores monitored data """
    monitor = models.CharField(_("monitor"), max_length=256,
            choices=ServiceMonitor.get_plugin_choices())
    content_type = models.ForeignKey(ContentType, verbose_name=_("content type"))
    object_id = models.PositiveIntegerField(_("object id"))
    created_at = models.DateTimeField(_("created"), default=timezone.now)
    value = models.DecimalField(_("value"), max_digits=16, decimal_places=2)
    
    content_object = GenericForeignKey()
    
    class Meta:
        get_latest_by = 'id'
        verbose_name_plural = _("monitor data")
    
    def __unicode__(self):
        return str(self.monitor)
    
    @cached_property
    def unit(self):
        return self.resource.unit


def create_resource_relation():
    class ResourceHandler(object):
        """ account.resources.web """
        def __getattr__(self, attr):
            """ get or build ResourceData """
            try:
                return self.obj.__resource_cache[attr]
            except AttributeError:
                self.obj.__resource_cache = {}
            except KeyError:
                pass
            try:
                data = self.obj.resource_set.get(resource__name=attr)
            except ResourceData.DoesNotExist:
                model = self.obj._meta.model_name
                resource = Resource.objects.get(
                    content_type__model=model,
                    name=attr,
                    is_active=True
                )
                data = ResourceData(
                    content_object=self.obj,
                    resource=resource,
                    allocated=resource.default_allocation
                )
            self.obj.__resource_cache[attr] = data
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
