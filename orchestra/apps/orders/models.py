from django.db import models
from django.db.models import Q
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
        qset = Q(plan__isnull=True)
        for plan in account.plans.all():
            qset |= Q(plan=plan)
        return self.filter(qset)


class Rate(models.Model):
    service = models.ForeignKey('orders.Service', verbose_name=_("service"),
            related_name='rates')
    plan = models.CharField(_("plan"), max_length=128, blank=True,
            choices=(('', _("Default")),) + settings.ORDERS_PLANS)
    quantity = models.PositiveIntegerField(_("quantity"), null=True, blank=True)
    value = models.DecimalField(_("value"), max_digits=12, decimal_places=2)
    
    objects = RateQuerySet.as_manager()
    
    class Meta:
        unique_together = ('service', 'plan', 'quantity')
    
    def __unicode__(self):
        return "{}-{}".format(str(self.value), self.quantity)


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
    PRICING_METHODS = {
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
    delayed_billing = models.CharField(_("delayed billing"), max_length=16,
            help_text=_("Period in which this service will be ignored for billing"),
            choices=(
                (NEVER, _("No delay (inmediate billing)")),
                (TEN_DAYS, _("Ten days")),
                (ONE_MONTH, _("One month")),
            ),
            default=ONE_MONTH, blank=True)
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
    orders_effect = models.CharField(_("orders effect"),  max_length=16,
            help_text=_("Defines the lookup behaviour when using orders for "
                        "the pricing rate computation of this service."),
            choices=(
                (REGISTER_OR_RENEW, _("Register or renew events")),
                (CONCURRENT, _("Active at every given time")),
            ),
            default=CONCURRENT)
    on_cancel = models.CharField(_("on cancel"), max_length=16,
            help_text=_("Defines the cancellation behaviour of this service"),
            choices=(
                (NOTHING, _("Nothing")),
                (DISCOUNT, _("Discount")),
                (COMPENSATE, _("Discount and compensate")),
                (REFOUND, _("Discount, compensate and refound")),
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
    trial_period = models.CharField(_("trial period"), max_length=16, blank=True,
            help_text=_("Period in which no charge will be issued"),
            choices=(
                (NEVER, _("No trial")),
                (TEN_DAYS, _("Ten days")),
                (ONE_MONTH, _("One month")),
            ),
            default=NEVER)
    refound_period = models.CharField(_("refound period"), max_length=16,
            help_text=_("Period in which automatic refound will be performed on "
                        "service cancellation"),
            choices=(
                (NEVER, _("Never refound")),
                (TEN_DAYS, _("Ten days")),
                (ONE_MONTH, _("One month")),
                (ALWAYS, _("Always refound")),
            ),
            default=NEVER, blank=True)
    
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
        rates = self.rates.by_account(order.account)
        if not rates:
            return self.nominal_price
        rates = self.rate_method(rates, metric)
        counter = 0
        if position is None:
            ant_counter = 0
            accumulated = 0
            for rate in self.get_rates(order.account, metric):
                counter += rate['number']
                if counter >= metric:
                    counter = metric
                    accumulated += (counter - ant_counter) * rate['price']
                    return accumulated
                ant_counter = counter
                accumulated += rate['price'] * rate['number']
        else:
            for rate in self.get_rates(order.account, metric):
                counter += rate['number']
                if counter >= position:
                    return rate['price']
    
    @property
    def rate_method(self, *args, **kwargs):
        return self.RATE_METHODS[self.rate_algorithm]


class OrderQuerySet(models.QuerySet):
    group_by = queryset.group_by
    
    def bill(self, **options):
        bills = []
        bill_backend = Order.get_bill_backend()
        qs = self.select_related('account', 'service')
        for account, services in qs.group_by('account', 'service'):
            bill_lines = []
            for service, orders in services:
                lines = service.handler.create_bill_lines(orders, **options)
                bill_lines.extend(lines)
            bills += bill_backend.create_bills(account, bill_lines)
        return bills
    
    def get_related(self):
        pass
    
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
    registered_on = models.DateField(_("registered on"), auto_now_add=True)
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


@receiver(pre_delete, dispatch_uid="orders.cancel_orders")
def cancel_orders(sender, **kwargs):
    if sender in services:
        instance = kwargs['instance']
        for order in Order.objects.by_object(instance).active():
            order.cancel()


@receiver(post_save, dispatch_uid="orders.update_orders")
@receiver(post_delete, dispatch_uid="orders.update_orders_post_delete")
def update_orders(sender, **kwargs):
    if sender not in [MetricStorage, LogEntry, Order, Service]:
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
