import logging
import sys

from django.db import models
from django.db.migrations.recorder import MigrationRecorder
from django.db.models import F, Q
from django.db.models.loading import get_model
from django.db.models.signals import pre_delete, post_delete, post_save
from django.dispatch import receiver
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core import caches, services, accounts
from orchestra.models import queryset
from orchestra.utils.apps import autodiscover
from orchestra.utils.python import import_class

from . import helpers, settings
from .handlers import ServiceHandler


logger = logging.getLogger(__name__)


class OrderQuerySet(models.QuerySet):
    group_by = queryset.group_by
    
    def bill(self, **options):
        # TODO classmethod?
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
    
    def givers(self, ini, end):
        return self.cancelled_and_billed().filter(billed_until__gt=ini, registered_on__lt=end)
    
    def cancelled_and_billed(self, exclude=False):
        qs = dict(cancelled_on__isnull=False, billed_until__isnull=False,
                  cancelled_on__lte=F('billed_until'))
        if exclude:
            return self.exclude(**qs)
        return self.filter(**qs)
    
    def pricing_orders(self, ini, end):
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
                    logger.info("CREATED new order id: {id}".format(id=order.id))
                else:
                    order = orders.get()
                order.update()
            elif orders:
                orders.get().cancel()
    
    @classmethod
    def get_bill_backend(cls):
        return import_class(settings.ORDERS_BILLING_BACKEND)()
    
    def update(self):
        instance = self.content_object
        handler = self.service.handler
        if handler.metric:
            metric = handler.get_metric(instance)
            if metric is not None:
                MetricStorage.store(self, metric)
        description = "{}: {}".format(handler.description, str(instance))
        logger.info("UPDATED order id: {id} description:{description}".format(
                    id=self.id, description=description))
        if self.description != description:
            self.description = description
            self.save()
    
    def cancel(self):
        self.cancelled_on = timezone.now()
        self.save()
        logger.info("CANCELLED order id: {id}".format(id=self.id))
    
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


_excluded_models = (MetricStorage, LogEntry, Order, ContentType, MigrationRecorder.Migration)

@receiver(post_delete, dispatch_uid="orders.cancel_orders")
def cancel_orders(sender, **kwargs):
    if sender not in _excluded_models:
        instance = kwargs['instance']
        if hasattr(instance, 'account'):
            for order in Order.objects.by_object(instance).active():
                order.cancel()
        else:
            related = helpers.get_related_objects(instance)
            if related and related != instance:
                Order.update_orders(related)


@receiver(post_save, dispatch_uid="orders.update_orders")
def update_orders(sender, **kwargs):
    if sender not in _excluded_models:
        instance = kwargs['instance']
        if hasattr(instance, 'account'):
            Order.update_orders(instance)
        else:
            related = helpers.get_related_objects(instance)
            if related and related != instance:
                Order.update_orders(related)


accounts.register(Order)
