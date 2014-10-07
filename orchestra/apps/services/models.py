import decimal

from django.db import models
from django.db.models import Q
from django.db.models.loading import get_model
from django.contrib.contenttypes.models import ContentType
from django.core.validators import ValidationError
from django.utils.functional import cached_property
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import ugettext_lazy as _

from orchestra.core import caches, services, accounts
from orchestra.models import queryset
#from orchestra.utils.apps import autodiscover

from . import settings, rating
from .handlers import ServiceHandler


class Plan(models.Model):
    name = models.CharField(_("plan"), max_length=128)
    is_default = models.BooleanField(_("default"), default=False)
    is_combinable = models.BooleanField(_("combinable"), default=True)
    allow_multiple = models.BooleanField(_("allow multiple"), default=False)
    
    def __unicode__(self):
        return self.name


class ContractedPlan(models.Model):
    plan = models.ForeignKey(Plan, verbose_name=_("plan"), related_name='contracts')
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='plans')
    
    class Meta:
        verbose_name_plural = _("plans")
    
    def __unicode__(self):
        return str(self.plan)
    
    def clean(self):
        if not self.pk and not self.plan.allow_multipls:
            if ContractedPlan.objects.filter(plan=self.plan, account=self.account).exists():
                raise ValidationError("A contracted plan for this account already exists")


class RateQuerySet(models.QuerySet):
    group_by = queryset.group_by
    
    def by_account(self, account):
        # Default allways selected
        return self.filter(
            Q(plan__is_default=True) |
            Q(plan__contracts__account=account)
        ).order_by('plan', 'quantity').select_related('plan')


class Rate(models.Model):
    service = models.ForeignKey('services.Service', verbose_name=_("service"),
            related_name='rates')
    plan = models.ForeignKey(Plan, verbose_name=_("plan"), related_name='rates')
    quantity = models.PositiveIntegerField(_("quantity"), null=True, blank=True)
    price = models.DecimalField(_("price"), max_digits=12, decimal_places=2)
    
    objects = RateQuerySet.as_manager()
    
    class Meta:
        unique_together = ('service', 'plan', 'quantity')
    
    def __unicode__(self):
        return "{}-{}".format(str(self.price), self.quantity)


autodiscover_modules('handlers')


class Service(models.Model):
    NEVER = ''
#    DAILY = 'DAILY'
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
    COMPENSATE = 'COMPENSATE'
    REFUND = 'REFUND'
    PREPAY = 'PREPAY'
    POSTPAY = 'POSTPAY'
    STEP_PRICE = 'STEP_PRICE'
    MATCH_PRICE = 'MATCH_PRICE'
    RATE_METHODS = {
        STEP_PRICE: rating.step_price,
        MATCH_PRICE: rating.match_price,
    }
    
    description = models.CharField(_("description"), max_length=256, unique=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_("content type"))
    match = models.CharField(_("match"), max_length=256, blank=True)
    handler_type = models.CharField(_("handler"), max_length=256, blank=True,
            help_text=_("Handler used for processing this Service. A handler "
                        "enables customized behaviour far beyond what options "
                        "here allow to."),
            choices=ServiceHandler.get_plugin_choices())
    is_active = models.BooleanField(_("active"), default=True)
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
    is_fee = models.BooleanField(_("fee"), default=False,
            help_text=_("Designates whether this service should be billed as "
                        " membership fee or not"))
    # Pricing
    metric = models.CharField(_("metric"), max_length=256, blank=True,
            help_text=_("Metric used to compute the pricing rate. "
                        "Number of orders is used when left blank."))
    nominal_price = models.DecimalField(_("nominal price"), max_digits=12,
            decimal_places=2)
    tax = models.PositiveIntegerField(_("tax"), choices=settings.SERVICES_SERVICE_TAXES,
            default=settings.SERVICES_SERVICE_DEFAUL_TAX)
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
                (STEP_PRICE, _("Step price")),
                (MATCH_PRICE, _("Match price")),
            ),
            default=STEP_PRICE)
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
                (COMPENSATE, _("Compensat")),
                (REFUND, _("Refund")),
            ),
            default=DISCOUNT)
#    on_broken_period = models.CharField(_("on broken period", max_length=16,
#            help_text=_("Defines the billing behaviour when periods are incomplete on register and on cancel"),
#            choices=(
#                (NOTHING, _("Nothing, period is atomic")),
#                (DISCOUNT, _("Bill partially")),
#                (COMPENSATE, _("Compensate on cancel")),
#                (REFUND, _("Refund on cancel")),
#            ),
#            default=DISCOUNT)
#    granularity = models.CharField(_("granularity"), max_length=16,
#            help_text=_("Defines the minimum size a period can be broken into"),
#            choices=(
#                (DAILY, _("One day")),
#                (MONTHLY, _("One month")),
#                (ANUAL, _("One year")),
#            ),
#            default=DAILY,
#    )
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
#    refund_period = models.CharField(_("refund period"), max_length=16,
#            help_text=_("Period in which automatic refund will be performed on "
#                        "service cancellation"),
#            choices=(
#                (NEVER, _("Never refund")),
#                (TEN_DAYS, _("Ten days")),
#                (ONE_MONTH, _("One month")),
#                (ALWAYS, _("Always refund")),
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
            ct = str(content_type)
            raise ValidationError(_("Content type must be equal to '%s'.") % ct)
        if not self.match:
            raise ValidationError(_("Match should be provided"))
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
    
    def get_price(self, account, metric, rates=None, position=None):
        """
        if position is provided an specific price for that position is returned,
        accumulated price is returned otherwise
        """
        if rates is None:
            rates = self.get_rates(account)
        if rates:
            rates =  self.rate_method(rates, metric)
        if not rates:
            rates = [{
                'quantity': metric,
                'price': self.nominal_price,
            }]
        counter = 0
        if position is None:
            ant_counter = 0
            accumulated = 0
            for rate in rates:
                counter += rate['quantity']
                if counter >= metric:
                    counter = metric
                    accumulated += (counter - ant_counter) * rate['price']
                    return decimal.Decimal(accumulated)
                ant_counter = counter
                accumulated += rate['price'] * rate['quantity']
        else:
            for rate in rates:
                counter += rate['quantity']
                if counter >= position:
                    return decimal.Decimal(rate['price'])
    
    def get_rates(self, account, cache=True):
        # rates are cached per account
        if not cache:
            return self.rates.by_account(account)
        if not hasattr(self, '__cached_rates'):
            self.__cached_rates = {}
        rates = self.__cached_rates.get(account.id, self.rates.by_account(account))
        return rates
    
    @property
    def rate_method(self):
        return self.RATE_METHODS[self.rate_algorithm]
    
    def update_orders(self):
        order_model = get_model(settings.SERVICES_ORDER_MODEL)
        related_model = self.content_type.model_class()
        for instance in related_model.objects.all().select_related('account'):
            order_model.update_orders(instance, service=self)


accounts.register(ContractedPlan)
services.register(ContractedPlan, menu=False)
