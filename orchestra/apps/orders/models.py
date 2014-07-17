from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from . import settings


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
    model = models.ForeignKey(ContentType, verbose_name=_("model"))
    match = models.CharField(_("match"), max_length=256)
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
    on_disable = models.CharField(_("on disable"), max_length=16,
            help_text=_("Defines the behaviour of this service when disabled"),
            choices=(
                (NOTHING, _("Nothing")),
                (DISCOUNT, _("Discount")),
                (REFOUND, _("Refound")),
            ),
            default=DISCOUNT)
    on_register = models.CharField(_("on register"), max_length=16,
            help_text=_("Defines the behaviour of this service on registration"),
            choices=(
                (NOTHING, _("Nothing")),
                (DISCOUNT, _("Discount (fixed BP)")),
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
    def get_services(cls, instance, **kwargs):
        cache = kwargs.get('cache', {})
        ct = ContentType.objects.get_for_model(type(instance))
        try:
            return cache[ct]
        except KeyError:
            cache[ct] = cls.objects.filter(model=ct, is_active=True)
            return cache[ct]
    
    def matches(self, instance):
        safe_locals = {
            'instance': instance
        }
        return eval(self.match, safe_locals)


class Order(models.Model):
    SAVE = 'SAVE'
    DELETE = 'DELETE'
    
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='orders')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    service = models.ForeignKey(Service, verbose_name=_("price"),
            related_name='orders')
    registered_on = models.DateTimeField(_("registered on"), auto_now_add=True)
    cancelled_on = models.DateTimeField(_("cancelled on"), null=True, blank=True)
    billed_on = models.DateTimeField(_("billed on"), null=True, blank=True)
    billed_until = models.DateTimeField(_("billed until"), null=True, blank=True)
    ignore = models.BooleanField(_("ignore"), default=False)
    description = models.TextField(_("description"), blank=True)
    
    content_object = generic.GenericForeignKey()
    
    def __unicode__(self):
        return str(self.service)
    
    def update(self):
        instance = self.content_object
        if self.service.metric:
            metric = self.service.get_metric(instance)
            self.store_metric(instance, metric)
        description = "{}: {}".format(self.service.description, str(instance))
        if self.description != description:
            self.description = description
            self.save()
    
    @classmethod
    def process_candidates(cls, candidates):
        cache = {}
        for candidate in candidates:
            instance = candidate.instance
            if candidate.action == cls.DELETE:
                cls.objects.filter_for_object(instance).cancel()
            else:
                for service in Service.get_services(instance, cache=cache):
                    print cache
                    if not instance.pk:
                        if service.matches(instance):
                            order = cls.objects.create(content_object=instance,
                                    account_id=instance.account_id, service=service)
                            order.update()
                    else:
                        ct = ContentType.objects.get_for_model(instance)
                        orders = cls.objects.filter(content_type=ct, service=service,
                                object_id=instance.pk)
                        if service.matches(instance):
                            if not orders:
                                order = cls.objects.create(content_object=instance,
                                        service=service, account_id=instance.account_id)
                            else:
                                order = orders.get()
                            order.update()
                        elif orders:
                            orders.get().cancel()


class MetricStorage(models.Model):
    order = models.ForeignKey(Order, verbose_name=_("order"))
    value = models.BigIntegerField(_("value"))
    date = models.DateTimeField(_("date"))
    
    def __unicode__(self):
        return self.order
