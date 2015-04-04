import datetime
import decimal
import logging

from django.db import models
from django.db.migrations.recorder import MigrationRecorder
from django.db.models import F, Q
from django.db.models.loading import get_model
from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.core import accounts, services
from orchestra.models import queryset
from orchestra.utils.python import import_class

from . import helpers, settings


logger = logging.getLogger(__name__)


class OrderQuerySet(models.QuerySet):
    group_by = queryset.group_by
    
    def bill(self, **options):
        bills = []
        bill_backend = Order.get_bill_backend()
        qs = self.select_related('account', 'service')
        commit = options.get('commit', True)
        for account, services in qs.group_by('account', 'service').items():
            bill_lines = []
            for service, orders in services.items():
                for order in orders:
                    # Saved for undoing support
                    order.old_billed_on = order.billed_on
                    order.old_billed_until = order.billed_until
                lines = service.handler.generate_bill_lines(orders, account, **options)
                bill_lines.extend(lines)
            # TODO make this consistent always returning the same fucking types
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
    
    def get_related(self, **options):
        """ returns related orders that could have a pricing effect """
        Service = get_model(settings.ORDERS_SERVICE_MODEL)
        conflictive = self.filter(service__metric='')
        conflictive = conflictive.exclude(service__billing_period=Service.NEVER)
        conflictive = conflictive.select_related('service').group_by('account_id', 'service')
        qs = Q()
        for account_id, services in conflictive.items():
            for service, orders in services.items():
                if not service.rates.exists():
                    continue
                ini = datetime.date.max
                end = datetime.date.min
                bp = None
                for order in orders:
                    bp = service.handler.get_billing_point(order, **options)
                    end = max(end, bp)
                    ini = min(ini, order.billed_until or order.registered_on)
                qs |= Q(
                    Q(service=service, account=account_id, registered_on__lt=end) & Q(
                        Q(billed_until__isnull=True) | Q(billed_until__lt=end)
                    ) & Q(
                        Q(cancelled_on__isnull=True) | Q(cancelled_on__gt=ini)
                    )
                )
        if not  qs:
            return self.model.objects.none()
        ids = self.values_list('id', flat=True)
        return self.model.objects.filter(qs).exclude(id__in=ids)
    
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
        return self.filter(cancelled_on__lte=timezone.now(), **kwargs)


class Order(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='orders')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    service = models.ForeignKey(settings.ORDERS_SERVICE_MODEL, verbose_name=_("service"),
            related_name='orders')
    registered_on = models.DateField(_("registered"), default=lambda: timezone.now())
    cancelled_on = models.DateField(_("cancelled"), null=True, blank=True)
    billed_on = models.DateField(_("billed"), null=True, blank=True)
    billed_until = models.DateField(_("billed until"), null=True, blank=True)
    ignore = models.BooleanField(_("ignore"), default=False)
    description = models.TextField(_("description"), blank=True)
    
    content_object = generic.GenericForeignKey()
    objects = OrderQuerySet.as_manager()
    
    class Meta:
        get_latest_by = 'id'
    
    def __str__(self):
        return str(self.service)
    
    @classmethod
    def update_orders(cls, instance, service=None, commit=True):
        updates = []
        if service is None:
            Service = get_model(settings.ORDERS_SERVICE_MODEL)
            services = Service.get_services(instance)
        else:
            services = [service]
        for service in services:
            orders = Order.objects.by_object(instance, service=service).active()
            if service.handler.matches(instance):
                if not orders:
                    account_id = getattr(instance, 'account_id', instance.pk)
                    if account_id is None:
                        # New account workaround -> user.account_id == None
                        continue
                    ignore = service.handler.get_ignore(instance)
                    order = cls(content_object=instance, service=service,
                            account_id=account_id, ignore=ignore)
                    if commit:
                        order.save()
                    updates.append((order, 'created'))
                    logger.info("CREATED new order id: {id}".format(id=order.id))
                else:
                    order = orders.get()
                    updates.append((order, 'updated'))
                if commit:
                    order.update()
            elif orders:
                order = orders.get()
                order.cancel(commit=commit)
                logger.info("CANCELLED order id: {id}".format(id=order.id))
                updates.append((order, 'cancelled'))
        return updates
    
    @classmethod
    def get_bill_backend(cls):
        return import_class(settings.ORDERS_BILLING_BACKEND)()
    
    def update(self):
        instance = self.content_object
        handler = self.service.handler
        metric = ''
        if handler.metric:
            metric = handler.get_metric(instance)
            if metric is not None:
                MetricStorage.store(self, metric)
            metric = ', metric:{}'.format(metric)
        description = handler.get_order_description(instance)
        logger.info("UPDATED order id:{id}, description:{description}{metric}".format(
                id=self.id, description=description, metric=metric).encode('ascii', 'ignore')
        )
        if self.description != description:
            self.description = description
            self.save(update_fields=['description'])
    
    def cancel(self, commit=True):
        self.cancelled_on = timezone.now()
        self.ignore = self.service.handler.get_order_ignore(self)
        if commit:
            self.save(update_fields=['cancelled_on', 'ignore'])
            logger.info("CANCELLED order id: {id}".format(id=self.id))
    
    def mark_as_ignored(self):
        self.ignore = True
        self.save(update_fields=['ignore'])
    
    def mark_as_not_ignored(self):
        self.ignore = False
        self.save(update_fields=['ignore'])
    
    def get_metric(self, *args, **kwargs):
        if kwargs.pop('changes', False):
            ini, end = args
            result = []
            prev = None
            for metric in self.metrics.filter(created_on__lt=end).order_by('id'):
                created = metric.created_on
                if created > ini:
                    cini = prev.created_on
                    if not result:
                        cini = ini
                    result.append((cini, created, prev.value))
                prev = metric
            if created < end:
                result.append((created, end, metric.value))
            return result
        if kwargs:
            raise AttributeError
        if len(args) == 2:
            ini, end = args
            metrics = self.metrics.filter(updated_on__lt=end, updated_on__gte=ini)
        elif len(args) == 1:
            date = args[0]
            date = datetime.date(year=date.year, month=date.month, day=date.day)
            date += datetime.timedelta(days=1)
            metrics = self.metrics.filter(updated_on__lt=date)
        elif not args:
            return self.metrics.latest('updated_on').value
        else:
            raise AttributeError
        try:
            return metrics.latest('updated_on').value
        except MetricStorage.DoesNotExist:
            return decimal.Decimal(0)


class MetricStorage(models.Model):
    """ Stores metric state for future billing """
    order = models.ForeignKey(Order, verbose_name=_("order"), related_name='metrics')
    value = models.DecimalField(_("value"), max_digits=16, decimal_places=2)
    created_on = models.DateField(_("created"), auto_now_add=True)
#    default=lambda: timezone.now())
    updated_on = models.DateTimeField(_("updated"))
    
    class Meta:
        get_latest_by = 'id'
    
    def __str__(self):
        return str(self.order)
    
    @classmethod
    def store(cls, order, value):
        now = timezone.now()
        try:
            last = cls.objects.filter(order=order).latest()
        except cls.DoesNotExist:
            cls.objects.create(order=order, value=value, updated_on=now)
        else:
            error = decimal.Decimal(str(settings.ORDERS_METRIC_ERROR))
            if value > last.value+error or value < last.value-error:
                cls.objects.create(order=order, value=value, updated_on=now)
            else:
                last.updated_on = now
                last.save(update_fields=['updated_on'])


accounts.register(Order)

#@receiver(pre_delete, dispatch_uid="orders.account_orders")
#def account_orders(sender, **kwargs):
#    account = kwargs['instance']
#    if isinstance(account, Order.account.field.rel.to):
#        account._deleted = True


# FIXME account deletion generates a integrity error
# TODO build a cache hash table {model: related, model: None}
@receiver(post_delete, dispatch_uid="orders.cancel_orders")
def cancel_orders(sender, **kwargs):
    if sender._meta.app_label not in settings.ORDERS_EXCLUDED_APPS:
        instance = kwargs['instance']
        # Account delete will delete all related orders, no need to maintain order consistency
#        if isinstance(instance, Order.account.field.rel.to):
#            return
        print('delete', sender, instance, instance.pk)
        if type(instance) in services:
            for order in Order.objects.by_object(instance).active():
                order.cancel()
        elif not hasattr(instance, 'account'):
            related = helpers.get_related_object(instance)
            # FIXME this shit returns objects that are already deleted
            # Indeterminate behaviour
            if related and related != instance:
#                if isinstance(related, Order.account.field.rel.to):
#                    return
                print('related', type(related), related, related.pk)
#                try:
                type(related).objects.get(pk=related.pk)
#                except related.DoesNotExist:
#                    print('not exists', type(related), related, related.pk)
                print([(str(a).encode('utf8'), b) for a, b in Order.update_orders(related)])

@receiver(post_save, dispatch_uid="orders.update_orders")
def update_orders(sender, **kwargs):
    if sender._meta.app_label not in settings.ORDERS_EXCLUDED_APPS:
        instance = kwargs['instance']
        if type(instance) in services:
            Order.update_orders(instance)
        elif not hasattr(instance, 'account'):
            related = helpers.get_related_object(instance)
            if related and related != instance:
                Order.update_orders(related)
