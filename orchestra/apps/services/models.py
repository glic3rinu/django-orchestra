import decimal

from django.contrib.contenttypes.models import ContentType
from django.core.validators import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.loading import get_model
from django.utils.functional import cached_property
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import ugettext_lazy as _

from orchestra.core import caches, services, accounts
from orchestra.core.validators import validate_name
from orchestra.models import queryset

from . import settings, rating
from .handlers import ServiceHandler


class Plan(models.Model):
    name = models.CharField(_("name"), max_length=32, unique=True, validators=[validate_name])
    verbose_name = models.CharField(_("verbose_name"), max_length=128, blank=True)
    is_default = models.BooleanField(_("default"), default=False,
        help_text=_("Designates whether this plan is used by default or not."))
    is_combinable = models.BooleanField(_("combinable"), default=True,
        help_text=_("Designates whether this plan can be combined with other plans or not."))
    allow_multiple = models.BooleanField(_("allow multiple"), default=False,
        help_text=_("Designates whether this plan allow for multiple contractions."))
    
    def __unicode__(self):
        return self.name
    
    def clean(self):
        self.verbose_name = self.verbose_name.strip()
    
    def get_verbose_name(self):
        return self.verbose_name or self.name


class ContractedPlan(models.Model):
    plan = models.ForeignKey(Plan, verbose_name=_("plan"), related_name='contracts')
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='plans')
    
    class Meta:
        verbose_name_plural = _("plans")
    
    def __unicode__(self):
        return str(self.plan)
    
    def clean(self):
        if not self.pk and not self.plan.allow_multiples:
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
    content_type = models.ForeignKey(ContentType, verbose_name=_("content type"),
            help_text=_("Content type of the related service objects."))
    match = models.CharField(_("match"), max_length=256, blank=True,
            help_text=_(
                "Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> "
                "that designates wheter a <tt>content_type</tt> object is related to this service "
                "or not, always evaluates <tt>True</tt> when left blank. "
                "Related instance can be instantiated with <tt>instance</tt> keyword or "
                "<tt>content_type.model_name</tt>.</br>"
                "<tt>&nbsp;databaseuser.type == 'MYSQL'</tt><br>"
                "<tt>&nbsp;miscellaneous.active and miscellaneous.service.name.lower() == 'domain .es'</tt><br>"
                "<tt>&nbsp;contractedplan.plan.name == 'association_fee''</tt><br>"
                "<tt>&nbsp;instance.active</tt>"))
    handler_type = models.CharField(_("handler"), max_length=256, blank=True,
            help_text=_("Handler used for processing this Service. A handler "
                        "enables customized behaviour far beyond what options "
                        "here allow to."),
            choices=ServiceHandler.get_plugin_choices())
    is_active = models.BooleanField(_("active"), default=True)
    ignore_superusers = models.BooleanField(_("ignore superusers"), default=True,
            help_text=_("Designates whether superuser orders are marked as ignored by default or not."))
    # Billing
    billing_period = models.CharField(_("billing period"), max_length=16,
            help_text=_("Renewal period for recurring invoicing."),
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
    is_fee = models.BooleanField(_("fee"), default=False,
            help_text=_("Designates whether this service should be billed as "
                        " membership fee or not"))
    order_description = models.CharField(_("Order description"), max_length=128, blank=True,
            help_text=_(
                "Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> "
                "used for generating the description for the bill lines of this services.<br>"
                "Defaults to <tt>'%s: %s' % (handler.description, instance)</tt>"
            ))
    # Pricing
    metric = models.CharField(_("metric"), max_length=256, blank=True,
            help_text=_(
                "Python <a href='https://docs.python.org/2/library/functions.html#eval'>expression</a> "
                "used for obtinging the <i>metric value</i> for the pricing rate computation. "
                "Number of orders is used when left blank. Related instance can be instantiated "
                "with <tt>instance</tt> keyword or <tt>content_type.model_name</tt>.<br>"
                "<tt>&nbsp;max((mailbox.resources.disk.allocated or 0) -1, 0)</tt><br>"
                "<tt>&nbsp;miscellaneous.amount</tt><br>"
                "<tt>&nbsp;max((account.resources.traffic.used or 0) -"
                " getattr(account.miscellaneous.filter(is_active=True,"
                " service__name='traffic prepay').last(), 'amount', 0), 0)</tt>"))
    nominal_price = models.DecimalField(_("nominal price"), max_digits=12,
            decimal_places=2)
    tax = models.PositiveIntegerField(_("tax"), choices=settings.SERVICES_SERVICE_TAXES,
            default=settings.SERVICES_SERVICE_DEFAUL_TAX)
    pricing_period = models.CharField(_("pricing period"), max_length=16,
            help_text=_("Time period that is used for computing the rate metric."),
            choices=(
                (BILLING_PERIOD, _("Same as billing period")),
                (MONTHLY, _("Monthly data")),
                (ANUAL, _("Anual data")),
            ),
            default=BILLING_PERIOD)
    rate_algorithm = models.CharField(_("rate algorithm"), max_length=16,
            help_text=_("Algorithm used to interprete the rating table."),
            choices=(
                (STEP_PRICE, _("Step price")),
                (MATCH_PRICE, _("Match price")),
            ),
            default=STEP_PRICE)
    on_cancel = models.CharField(_("on cancel"), max_length=16,
            help_text=_("Defines the cancellation behaviour of this service."),
            choices=(
                (NOTHING, _("Nothing")),
                (DISCOUNT, _("Discount")),
                (COMPENSATE, _("Compensat")),
                (REFUND, _("Refund")),
            ),
            default=DISCOUNT)
    payment_style = models.CharField(_("payment style"), max_length=16,
            help_text=_("Designates whether this service should be paid after "
                        "consumtion (postpay/on demand) or prepaid."),
            choices=(
                (PREPAY, _("Prepay")),
                (POSTPAY, _("Postpay (on demand)")),
            ),
            default=PREPAY)
    
    def __unicode__(self):
        return self.description
    
    @classmethod
    def get_services(cls, instance):
        cache = caches.get_request_cache()
        ct = ContentType.objects.get_for_model(instance)
        key = 'services.Service-%i' % ct.pk
        services = cache.get(key)
        if services is None:
            services = cls.objects.filter(content_type=ct, is_active=True)
            cache.set(key, services)
        return services
    
    @cached_property
    def handler(self):
        """ Accessor of this service handler instance """
        if self.handler_type:
            return ServiceHandler.get_plugin(self.handler_type)(self)
        return ServiceHandler(self)
    
    def clean(self):
        self.description = self.description.strip()
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
    
    def update_orders(self, commit=True):
        order_model = get_model(settings.SERVICES_ORDER_MODEL)
        related_model = self.content_type.model_class()
        updates = []
        for instance in related_model.objects.all().select_related('account'):
            updates += order_model.update_orders(instance, service=self, commit=commit)
        return updates


accounts.register(ContractedPlan)
services.register(ContractedPlan, menu=False)
