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

from . import settings, helpers
from .handlers import ServiceHandler


autodiscover('handlers')


class Service(models.Model):
    NEVER = 'NEVER'
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
    PREPAY = 'PREPAY'
    POSTPAY = 'POSTPAY'
    BEST_PRICE = 'BEST_PRICE'
    PROGRESSIVE_PRICE = 'PROGRESSIVE_PRICE'
    MATCH_PRICE = 'MATCH_PRICE'
    
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
            default=ANUAL)
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
            default=ONE_MONTH)
    is_fee = models.BooleanField(_("is fee"), default=False,
            help_text=_("Designates whether this service should be billed as "
                        " membership fee or not"))
    # Pricing
    metric = models.CharField(_("metric"), max_length=256, blank=True,
            help_text=_("Metric used to compute the pricing rate. "
                        "Number of orders is used when left blank."))
    tax = models.IntegerField(_("tax"), choices=settings.ORDERS_SERVICE_TAXES,
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
                (BEST_PRICE, _("Best price")),
                (PROGRESSIVE_PRICE, _("Progressive price")),
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
                (REFOUND, _("Refound")),
            ),
            default=DISCOUNT)
    # TODO remove, orders are not disabled (they are cancelled user.is_active)
#    on_disable = models.CharField(_("on disable"), max_length=16,
#            help_text=_("Defines the behaviour of this service when disabled"),
#            choices=(
#                (NOTHING, _("Nothing")),
#                (DISCOUNT, _("Discount")),
#                (REFOUND, _("Refound")),
#            ),
#            default=DISCOUNT)
#    on_register = models.CharField(_("on register"), max_length=16,
#            help_text=_("Defines the behaviour of this service on registration"),
#            choices=(
#                (NOTHING, _("Nothing")),
#                (DISCOUNT, _("Discount (fixed BP)")),
#            ),
#            default=DISCOUNT)
    payment_style = models.CharField(_("payment style"), max_length=16,
            help_text=_("Designates whether this service should be paid after "
                        "consumtion (postpay/on demand) or prepaid"),
            choices=(
                (PREPAY, _("Prepay")),
                (POSTPAY, _("Postpay (on demand)")),
            ),
            default=PREPAY)
    trial_period = models.CharField(_("trial period"), max_length=16,
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
            default=ONE_MONTH)
    
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


class OrderQuerySet(models.QuerySet):
    group_by = queryset.group_by
    
    def bill(self, **options):
        for account, services in self.group_by('account_id', 'service_id'):
            bill_lines = []
            for service, orders in services:
                lines = helpers.create_bill_lines(service, orders, **options)
                bill_lines.extend(lines)
            helpers.create_bills(account, bill_lines)
    
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
    registered_on = models.DateTimeField(_("registered on"), auto_now_add=True)
    cancelled_on = models.DateTimeField(_("cancelled on"), null=True, blank=True)
    billed_on = models.DateTimeField(_("billed on"), null=True, blank=True)
    billed_until = models.DateTimeField(_("billed until"), null=True, blank=True)
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
    
    def cancel(self):
        self.cancelled_on = timezone.now()
        self.save()


class MetricStorage(models.Model):
    order = models.ForeignKey(Order, verbose_name=_("order"))
    value = models.BigIntegerField(_("value"))
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    updated_on = models.DateTimeField(_("updated on"), auto_now=True)
    
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
