import decimal

from django.contrib.contenttypes.models import ContentType
from django.core.validators import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.loading import get_model
from django.utils.functional import cached_property
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import ugettext_lazy as _

from orchestra.core import caches, validators
from orchestra.core.validators import validate_name
from orchestra.models import queryset

from . import settings
from .handlers import ServiceHandler


autodiscover_modules('handlers')


class Service(models.Model):
    NEVER = ''
#    DAILY = 'DAILY'
    MONTHLY = 'MONTHLY'
    ANUAL = 'ANUAL'
    ONE_DAY = 'ONE_DAY'
    TWO_DAYS = 'TWO_DAYS'
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
                "<tt>&nbsp;miscellaneous.active and miscellaneous.identifier.endswith(('.org', '.net', '.com'))</tt><br>"
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
    ignore_period = models.CharField(_("ignore period"), max_length=16, blank=True,
            help_text=_("Period in which orders will be ignored if cancelled. "
                        "Useful for designating <i>trial periods</i>"),
            choices=(
                (NEVER, _("Never")),
                (ONE_DAY, _("One day")),
                (TWO_DAYS, _("Two days")),
                (TEN_DAYS, _("Ten days")),
                (ONE_MONTH, _("One month")),
            ),
            default=settings.SERVICES_DEFAULT_IGNORE_PERIOD)
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
                " service__name='traffic-prepay').last(), 'amount', 0), 0)</tt>"))
    nominal_price = models.DecimalField(_("nominal price"), max_digits=12,
            decimal_places=2)
    tax = models.PositiveIntegerField(_("tax"), choices=settings.SERVICES_SERVICE_TAXES,
            default=settings.SERVICES_SERVICE_DEFAULT_TAX)
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
            # TODO this should be dynamic, retrieved from rate (plans) app
            choices=(
                ('STEP_PRICE', _("Step price")),
                ('MATCH_PRICE', _("Match price")),
            ),
            default='STEP_PRICE')
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
        if hasattr(self, 'content_type'):
            validators.all_valid({
                'content_type': (self.handler.validate_content_type, self),
                'match': (self.handler.validate_match, self),
                'metric': (self.handler.validate_metric, self),
            })
        
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
        rate_model = type(self).rates.related.model
        return rate_model.get_methods()[self.rate_algorithm]
    
    def update_orders(self, commit=True):
        order_model = get_model(settings.SERVICES_ORDER_MODEL)
        related_model = self.content_type.model_class()
        updates = []
        for instance in related_model.objects.all().select_related('account'):
            updates += order_model.update_orders(instance, service=self, commit=commit)
        return updates
