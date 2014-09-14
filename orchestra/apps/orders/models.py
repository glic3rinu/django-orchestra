import sys

from django.db import models
from django.db.migrations.recorder import MigrationRecorder
from django.db.models import F, Q
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

from . import helpers, settings, pricing
from .handlers import ServiceHandler


class Plan(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='plans')
    name = models.CharField(_("plan"), max_length=128,
            choices=settings.ORDERS_PLANS,
            default=settings.ORDERS_DEFAULT_PLAN)
    
    def __unicode__(self):
        return self.name


class RateQuerySet(models.QuerySet):
    group_by = queryset.group_by
    
    def by_account(self, account):
        # Default allways selected
        qset = Q(plan='')
        for plan in account.plans.all():
            qset |= Q(plan=plan)
        return self.filter(qset)


class Rate(models.Model):
    service = models.ForeignKey('orders.Service', verbose_name=_("service"),
            related_name='rates')
    plan = models.CharField(_("plan"), max_length=128, blank=True,
            choices=(('', _("Default")),) + settings.ORDERS_PLANS)
    quantity = models.PositiveIntegerField(_("quantity"), null=True, blank=True)
    price = models.DecimalField(_("price"), max_digits=12, decimal_places=2)
    
    objects = RateQuerySet.as_manager()
    
    class Meta:
        unique_together = ('service', 'plan', 'quantity')
    
    def __unicode__(self):
        return "{}-{}".format(str(self.price), self.quantity)


autodiscover('handlers')


class Service(models.Model):
    NEVER = ''
    MONTHLY = 'MONTHLY'
    ANUAL = 'ANUAL'
    TEN_DAYS = 'TEN_DAYS'
    ONE_MONTH = 'ONE_MONTH'
    ALWAYS = 'ALWAYS'
    ON_REGISTER = 'ON_REGISTER'
    FIXED_DATE = 'ON_FIXED_DATE'
    BILLING_PERIOD = 'BILLING_PERIOD'
    REGISTER_OR_RENEW = 'REGISTER_OR_RENEW'
    CONCURRENT = 'CONCURRENT'
    NOTHING = 'NOTHING'
    DISCOUNT = 'DISCOUNT'
    REFOUND = 'REFOUND'
    COMPENSATE = 'COMPENSATE'
    PREPAY = 'PREPAY'
    POSTPAY = 'POSTPAY'
    BEST_PRICE = 'BEST_PRICE'
    PROGRESSIVE_PRICE = 'PROGRESSIVE_PRICE'
    MATCH_PRICE = 'MATCH_PRICE'
    RATE_METHODS = {
        BEST_PRICE: pricing.best_price,
        MATCH_PRICE: pricing.match_price,
    }
    
    description = models.CharField(_("description"), max_length=256, unique=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_("content type"))
    match = models.CharField(_("match"), max_length=256, blank=True)
    handler_type = models.CharField(_("handler"), max_length=256, blank=True,
            help_text=_("Handler used for processing this Service. A handler "
                        "enables customized behaviour far beyond what options "
                        "here allow to."),
            choices=ServiceHandler.get_plugin_choices())
    is_active = models.BooleanField(_("is active"), default=True)
    # Billing
    billing_period = models.CharField(_("billing period"), max_length=16,
            help_text=_("Renewal period for recurring invoicing"),
            choices=(
                (NEVER, _("One time service")),
                (MONTHLY, _("Monthly billing")),
                (ANUAL, _("Anual billing")),
            ),
            default=ANUAL, blank=True)
    billing_point = models.CharField(_("billing point"), max_length=16,
            help_text=_("Reference point for calculating the renewal date "
                        "on recurring invoices"),
            choices=(
                (ON_REGISTER, _("Registration date")),
                (FIXED_DATE, _("Fixed billing date")),
            ),
            default=FIXED_DATE)
#    delayed_billing = models.CharField(_("delayed billing"), max_length=16,
#            help_text=_("Period in which this service will be ignored for billing"),
#            choices=(
#                (NEVER, _("No delay (inmediate billing)")),
#                (TEN_DAYS, _("Ten days")),
#                (ONE_MONTH, _("One month")),
#            ),
#            default=ONE_MONTH, blank=True)
    is_fee = models.BooleanField(_("is fee"), default=False,
            help_text=_("Designates whether this service should be billed as "
                        " membership fee or not"))
    # Pricing
    metric = models.CharField(_("metric"), max_length=256, blank=True,
            help_text=_("Metric used to compute the pricing rate. "
                        "Number of orders is used when left blank."))
    nominal_price = models.DecimalField(_("nominal price"), max_digits=12,
            decimal_places=2)
    tax = models.PositiveIntegerField(_("tax"), choices=settings.ORDERS_SERVICE_TAXES,
            default=settings.ORDERS_SERVICE_DEFAUL_TAX)
    pricing_period = models.CharField(_("pricing period"), max_length=16,
            help_text=_("Period used for calculating the metric used on the "
                        "pricing rate"),
            choices=(
                (BILLING_PERIOD, _("Same as billing period")),
                (MONTHLY, _("Monthly data")),
                (ANUAL, _("Anual data")),
            ),
            default=BILLING_PERIOD)
    rate_algorithm = models.CharField(_("rate algorithm"), max_length=16,
            help_text=_("Algorithm used to interprete the rating table"),
            choices=(
                (BEST_PRICE, _("Best progressive price")),
                (PROGRESSIVE_PRICE, _("Conservative progressive price")),
                (MATCH_PRICE, _("Match price")),
            ),
            default=BEST_PRICE)
#    orders_effect = models.CharField(_("orders effect"),  max_length=16,
#            help_text=_("Defines the lookup behaviour when using orders for "
#                        "the pricing rate computation of this service."),
#            choices=(
#                (REGISTER_OR_RENEW, _("Register or renew events")),
#                (CONCURRENT, _("Active at every given time")),
#            ),
#            default=CONCURRENT)
    on_cancel = models.CharField(_("on cancel"), max_length=16,
            help_text=_("Defines the cancellation behaviour of this service"),
            choices=(
                (NOTHING, _("Nothing")),
                (DISCOUNT, _("Discount")),
                (COMPENSATE, _("Discount and compensate")),
            ),
            default=DISCOUNT)
    payment_style = models.CharField(_("payment style"), max_length=16,
            help_text=_("Designates whether this service should be paid after "
                        "consumtion (postpay/on demand) or prepaid"),
            choices=(
                (PREPAY, _("Prepay")),
                (POSTPAY, _("Postpay (on demand)")),
            ),
            default=PREPAY)
#    trial_period = models.CharField(_("trial period"), max_length=16, blank=True,
#            help_text=_("Period in which no charge will be issued"),
#            choices=(
#                (NEVER, _("No trial")),
#                (TEN_DAYS, _("Ten days")),
#                (ONE_MONTH, _("One month")),
#            ),
#            default=NEVER)
#    refound_period = models.CharField(_("refound period"), max_length=16,
#            help_text=_("Period in which automatic refound will be performed on "
#                        "service cancellation"),
#            choices=(
#                (NEVER, _("Never refound")),
#                (TEN_DAYS, _("Ten days")),
#                (ONE_MONTH, _("One month")),
#                (ALWAYS, _("Always refound")),
#            ),
#            default=NEVER, blank=True)
    
    def __unicode__(self):
        return self.description
    
    @classmethod
    def get_services(cls, instance):
        cache = caches.get_request_cache()
        ct = ContentType.objects.get_for_model(instance)
        services = cache.get(ct)
        if services is None:
            services = cls.objects.filter(content_type=ct, is_active=True)
            cache.set(ct, services)
        return services
    
    # FIXME some times caching is nasty, do we really have to? make get_plugin more efficient?
    # @property
    @cached_property
    def handler(self):
        """ Accessor of this service handler instance """
        if self.handler_type:
            return ServiceHandler.get_plugin(self.handler_type)(self)
        return ServiceHandler(self)
    
    def clean(self):
        content_type = self.handler.get_content_type()
        if self.content_type != content_type:
            msg =_("Content type must be equal to '%s'.") % str(content_type)
            raise ValidationError(msg)
        if not self.match:
            msg =_("Match should be provided")
            raise ValidationError(msg)
        try:
            obj = content_type.model_class().objects.all()[0]
        except IndexError:
            pass
        else:
            attr = None
            try:
                bool(self.handler.matches(obj))
            except Exception as exception:
                attr = "Matches"
            try:
                metric = self.handler.get_metric(obj)
                if metric is not None:
                    int(metric)
            except Exception as exception:
                attr = "Get metric"
            if attr is not None:
                name = type(exception).__name__
                message = exception.message
                msg = "{0} {1}: {2}".format(attr, name, message)
                raise ValidationError(msg)
    
    def get_pricing_period(self):
        if self.pricing_period == self.BILLING_PERIOD:
            return self.billing_period
        return self.pricing_period
    
    def get_price(self, order, metric, position=None):
        """
        if position is provided an specific price for that position is returned,
        accumulated price is returned otherwise
        """
        rates = self.get_rates(order.account, metric)
        counter = 0
        if position is None:
            ant_counter = 0
            accumulated = 0
            for rate in rates:
                counter += rate['quantity']
                if counter >= metric:
                    counter = metric
                    accumulated += (counter - ant_counter) * rate['price']
                    return float(accumulated)
                ant_counter = counter
                accumulated += rate['price'] * rate['quantity']
        else:
            for rate in rates:
                counter += rate['quantity']
                if counter >= position:
                    return float(rate['price'])
    
    
    def get_rates(self, account, metric):
        if not hasattr(self, '__cached_rates'):
            self.__cached_rates = {}
        if account.id in self.__cached_rates:
            rates, cache = self.__cached_rates.get(account.id)
        else:
            rates = self.rates.by_account(account)
            cache = {}
            if not rates:
                rates = [{
                    'quantity': sys.maxint,
                    'price': self.nominal_price,
                }]
                self.__cached_rates[account.id] = (rates, cache)
                return rates
            self.__cached_rates[account.id] = (rates, cache)
        # Caching depends on the specific rating method
        return self.rate_method(rates, metric, cache=cache)
    
    @property
    def rate_method(self):
        return self.RATE_METHODS[self.rate_algorithm]


class OrderQuerySet(models.QuerySet):
    group_by = queryset.group_by
    
    def bill(self, **options):
        bills = []
        bill_backend = Order.get_bill_backend()
        qs = self.select_related('account', 'service')
        commit = options.get('commit', True)
        for account, services in qs.group_by('account', 'service'):
            bill_lines = []
            for service, orders in services:
                lines = service.handler.generate_bill_lines(orders, **options)
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
    service = models.ForeignKey(Service, verbose_name=_("service"),
            related_name='orders')
    registered_on = models.DateField(_("registered on"), auto_now_add=True) # TODO datetime field?
    cancelled_on = models.DateField(_("cancelled on"), null=True, blank=True)
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
        MetricStorage, LogEntry, Order, Service, ContentType, MigrationRecorder.Migration
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
accounts.register(Plan)
services.register(Plan, menu=False)
