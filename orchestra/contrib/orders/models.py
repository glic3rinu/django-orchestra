import datetime
import decimal
import logging

from django.db import models
from django.db.models import F, Q, Sum
from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.models import queryset
from orchestra.utils.python import import_class

from . import settings


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
        # TODO remove if commit and always return unique elemenets (set()) when the other todo is fixed
        if commit:
            return list(set(bills))
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
        Service = apps.get_model(settings.ORDERS_SERVICE_MODEL)
        conflictive = self.filter(service__metric='')
        conflictive = conflictive.exclude(service__billing_period=Service.NEVER)
        # Exclude rates null or all rates with quantity 0
        conflictive = conflictive.annotate(quantity_sum=Sum('service__rates__quantity'))
        conflictive = conflictive.exclude(quantity_sum=0).select_related('service').distinct()
        qs = Q()
        for account_id, services in conflictive.group_by('account_id', 'service').items():
            for service, orders in services.items():
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
    
    def update_by_instance(self, instance, service=None, commit=True):
        updates = []
        if service is None:
            Service = apps.get_model(settings.ORDERS_SERVICE_MODEL)
            services = Service.objects.filter_by_instance(instance)
        else:
            services = [service]
        for service in services:
            orders = Order.objects.by_object(instance, service=service)
            orders = orders.select_related('service').active()
            if service.handler.matches(instance):
                if not orders:
                    account_id = getattr(instance, 'account_id', instance.pk)
                    if account_id is None:
                        # New account workaround -> user.account_id == None
                        continue
                    ignore = service.handler.get_ignore(instance)
                    order = self.model(
                        content_object=instance,
                        content_object_repr=str(instance),
                        service=service,
                        account_id=account_id,
                        ignore=ignore)
                    if commit:
                        order.save()
                    updates.append((order, 'created'))
                    logger.info("CREATED new order id: {id}".format(id=order.id))
                else:
                    if len(orders) > 1:
                        raise ValueError("A single active order was expected.")
                    order = orders[0]
                    updates.append((order, 'updated'))
                if commit:
                    order.update()
            elif orders:
                if len(orders) > 1:
                    raise ValueError("A single active order was expected.")
                order = orders[0]
                order.cancel(commit=commit)
                logger.info("CANCELLED order id: {id}".format(id=order.id))
                updates.append((order, 'cancelled'))
        return updates


class Order(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
        related_name='orders')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    service = models.ForeignKey(settings.ORDERS_SERVICE_MODEL, verbose_name=_("service"),
        related_name='orders')
    registered_on = models.DateField(_("registered"), default=timezone.now, db_index=True)
    cancelled_on = models.DateField(_("cancelled"), null=True, blank=True)
    billed_on = models.DateField(_("billed"), null=True, blank=True)
    billed_metric = models.DecimalField(_("billed metric"), max_digits=16, decimal_places=2,
        null=True, blank=True)
    billed_until = models.DateField(_("billed until"), null=True, blank=True)
    ignore = models.BooleanField(_("ignore"), default=False)
    description = models.TextField(_("description"), blank=True)
    content_object_repr = models.CharField(_("content object representation"), max_length=256,
        editable=False, help_text=_("Used for searches."))
    
    content_object = GenericForeignKey()
    objects = OrderQuerySet.as_manager()
    
    class Meta:
        get_latest_by = 'id'
        index_together = (
            ('content_type', 'object_id'),
        )
    
    def __str__(self):
        return str(self.service)
    
    @classmethod
    def get_bill_backend(cls):
        return import_class(settings.ORDERS_BILLING_BACKEND)()
    
    def clean(self):
        if self.billed_on and self.billed_on < self.registered_on:
            raise ValidationError(_("Billed date can not be earlier than registered on."))
        if self.billed_until and not self.billed_on:
            raise ValidationError(_("Billed on is missing while billed until is being provided."))
    
    def update(self):
        instance = self.content_object
        if instance is None:
            return
        handler = self.service.handler
        metric = ''
        if handler.metric:
            metric = handler.get_metric(instance)
            if metric is not None:
                MetricStorage.objects.store(self, metric)
            metric = ', metric:{}'.format(metric)
        description = handler.get_order_description(instance)
        logger.info("UPDATED order id:{id}, description:{description}{metric}".format(
            id=self.id, description=description, metric=metric).encode('ascii', 'replace')
        )
        update_fields = []
        if self.description != description:
            self.description = description
            update_fields.append('description')
        content_object_repr = str(instance)
        if self.content_object_repr != content_object_repr:
            self.content_object_repr = content_object_repr
            update_fields.append('content_object_repr')
        if update_fields:
            self.save(update_fields=update_fields)
    
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
                    if prev is None:
                        raise ValueError("Metric storage information for order %i is inconsistent." % self.id)
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
            # Slot
            ini, end = args
            metrics = self.metrics.filter(created_on__lt=end, updated_on__gte=ini)
        elif len(args) == 1:
            # On effect on date
            date = args[0]
            date = datetime.date(year=date.year, month=date.month, day=date.day)
            date += datetime.timedelta(days=1)
            metrics = self.metrics.filter(created_on__lte=date)
        elif not args:
            return self.metrics.latest('updated_on').value
        else:
            raise AttributeError
        try:
            return metrics.latest('updated_on').value
        except MetricStorage.DoesNotExist:
            return decimal.Decimal(0)


class MetricStorageQuerySet(models.QuerySet):
    def store(self, order, value):
        now = timezone.now()
        try:
            last = self.filter(order=order).latest()
        except self.model.DoesNotExist:
            self.create(order=order, value=value, updated_on=now)
        else:
            # Metric storage has per-day granularity (last value of the day is what counts)
            if last.created_on == now.date():
                last.value = value
                last.updated_on = now
                last.save()
            else:
                error = decimal.Decimal(str(settings.ORDERS_METRIC_ERROR))
                if (value > last.value+error or value < last.value-error) or (value == 0 and last.value > 0):
                    self.create(order=order, value=value, updated_on=now)
                else:
                    last.updated_on = now
                    last.save(update_fields=['updated_on'])


class MetricStorage(models.Model):
    """ Stores metric state for future billing """
    order = models.ForeignKey(Order, verbose_name=_("order"), related_name='metrics')
    value = models.DecimalField(_("value"), max_digits=16, decimal_places=2)
    created_on = models.DateField(_("created"), auto_now_add=True, editable=True)
    # TODO time field?
    updated_on = models.DateTimeField(_("updated"))
    
    objects = MetricStorageQuerySet.as_manager()
    
    class Meta:
        get_latest_by = 'id'
    
    def __str__(self):
        return str(self.order)
