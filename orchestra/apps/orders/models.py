import sys

from django.core.exceptions import ValidationError
from django.db import models
from django.db.migrations.recorder import MigrationRecorder
from django.db.models import F, Q
from django.db.models.loading import get_model
from django.db.models.signals import pre_delete, post_delete, post_save
from django.dispatch import receiver
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.validators import ValidationError
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core import caches, services, accounts
from orchestra.models import queryset
from orchestra.utils.apps import autodiscover
from orchestra.utils.python import import_class

from . import helpers, settings
from .handlers import ServiceHandler


class OrderQuerySet(models.QuerySet):
    group_by = queryset.group_by
    
    def bill(self, **options):
        bills = []
        bill_backend = Order.get_bill_backend()
        qs = self.select_related('account', 'service')
        commit = options.get('commit', True)
        for account, services in qs.group_by('account', 'service').iteritems():
            bill_lines = []
            for service, orders in services.iteritems():
                lines = service.handler.generate_bill_lines(orders, account, **options)
                bill_lines.extend(lines)
            if commit:
                bills += bill_backend.create_bills(account, bill_lines, **options)
            else:
                bills += [(account, bill_lines)]
        return bills
    
    def filter_givers(self, ini, end):
        return self.filter(
            cancelled_on__isnull=False, billed_until__isnull=False,
            cancelled_on__lte=F('billed_until'), billed_until__gt=ini,
            registered_on__lt=end)
    
    def filter_pricing_orders(self, ini, end):
        return self.filter(billed_until__isnull=False, billed_until__gt=ini,
            registered_on__lt=end)
    
    def by_object(self, obj, **kwargs):
        ct = ContentType.objects.get_for_model(obj)
        return self.filter(object_id=obj.pk, content_type=ct, **kwargs)
    
    def active(self, **kwargs):
        """ return active orders """
        return self.filter(
            Q(cancelled_on__isnull=True) | Q(cancelled_on__gt=timezone.now())
        ).filter(**kwargs)
    
    def inactive(self, **kwargs):
        """ return inactive orders """
        return self.filter(cancelled_on__lt=timezone.now(), **kwargs)


class Order(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='orders')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    service = models.ForeignKey(settings.ORDERS_SERVICE_MODEL,
            verbose_name=_("service"), related_name='orders')
    registered_on = models.DateField(_("registered"), auto_now_add=True) # TODO datetime field?
    cancelled_on = models.DateField(_("cancelled"), null=True, blank=True)
    billed_on = models.DateField(_("billed on"), null=True, blank=True)
    billed_until = models.DateField(_("billed until"), null=True, blank=True)
    ignore = models.BooleanField(_("ignore"), default=False)
    description = models.TextField(_("description"), blank=True)
    
    content_object = generic.GenericForeignKey()
    objects = OrderQuerySet.as_manager()
    
    def __unicode__(self):
        return str(self.service)
    
    def update(self):
        instance = self.content_object
        handler = self.service.handler
        if handler.metric:
            metric = handler.get_metric(instance)
            if metric is not None:
                MetricStorage.store(self, metric)
        description = "{}: {}".format(handler.description, str(instance))
        if self.description != description:
            self.description = description
            self.save()
    
    @classmethod
    def update_orders(cls, instance):
        Service = get_model(*settings.ORDERS_SERVICE_MODEL.split('.'))
        for service in Service.get_services(instance):
            orders = Order.objects.by_object(instance, service=service).active()
            if service.handler.matches(instance):
                if not orders:
                    account_id = getattr(instance, 'account_id', instance.pk)
                    if account_id is None:
                        # New account workaround -> user.account_id == None
                        continue
                    order = cls.objects.create(content_object=instance,
                            service=service, account_id=account_id)
                else:
                    order = orders.get()
                order.update()
            elif orders:
                orders.get().cancel()
    
    @classmethod
    def get_bill_backend(cls):
        return import_class(settings.ORDERS_BILLING_BACKEND)()
    
    def cancel(self):
        self.cancelled_on = timezone.now()
        self.save()
    
    def get_metric(self, ini, end):
        return MetricStorage.get(self, ini, end)


class MetricStorage(models.Model):
    order = models.ForeignKey(Order, verbose_name=_("order"))
    value = models.BigIntegerField(_("value"))
    created_on = models.DateField(_("created on"), auto_now_add=True)
    updated_on = models.DateField(_("updated on"), auto_now=True)
    
    class Meta:
        get_latest_by = 'created_on'
    
    def __unicode__(self):
        return unicode(self.order)
    
    @classmethod
    def store(cls, order, value):
        try:
            metric = cls.objects.filter(order=order).latest()
        except cls.DoesNotExist:
            cls.objects.create(order=order, value=value)
        else:
            if metric.value != value:
                cls.objects.create(order=order, value=value)
            else:
                metric.save()
    
    @classmethod
    def get(cls, order, ini, end):
        try:
            return cls.objects.filter(order=order, updated_on__lt=end,
                    updated_on__gte=ini).latest('updated_on').value
        except cls.DoesNotExist:
            return 0


# TODO If this happens to be very costly then, consider an additional
#      implementation when runnning within a request/Response cycle, more efficient :)
@receiver(pre_delete, dispatch_uid="orders.cancel_orders")
def cancel_orders(sender, **kwargs):
    if sender in services:
        instance = kwargs['instance']
        for order in Order.objects.by_object(instance).active():
            order.cancel()


@receiver(post_save, dispatch_uid="orders.update_orders")
@receiver(post_delete, dispatch_uid="orders.update_orders_post_delete")
def update_orders(sender, **kwargs):
    exclude = (
        MetricStorage, LogEntry, Order, ContentType, MigrationRecorder.Migration
    )
    if sender not in exclude:
        instance = kwargs['instance']
        if instance.pk:
            # post_save
            Order.update_orders(instance)
        related = helpers.get_related_objects(instance)
        if related:
            Order.update_orders(related)


accounts.register(Order)
