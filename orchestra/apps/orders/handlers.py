import calendar

from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.utils import plugins

from .helpers import get_register_or_cancel_events, get_register_or_renew_events


class ServiceHandler(plugins.Plugin):
    """
    Separates all the logic of billing handling from the model allowing to better
    customize its behaviout
    """
    
    model = None
    
    __metaclass__ = plugins.PluginMount
    
    def __init__(self, service):
        self.service = service
    
    def __getattr__(self, attr):
        return getattr(self.service, attr)
    
    @classmethod
    def get_plugin_choices(cls):
        choices = super(ServiceHandler, cls).get_plugin_choices()
        return [('', _("Default"))] + choices
    
    def get_content_type(self):
        if not self.model:
            return self.content_type
        app_label, model = self.model.split('.')
        return ContentType.objects.get_by_natural_key(app_label, model.lower())
    
    def matches(self, instance):
        safe_locals = {
            instance._meta.model_name: instance
        }
        return eval(self.match, safe_locals)
    
    def get_metric(self, instance):
        if self.metric:
            safe_locals = {
                instance._meta.model_name: instance
            }
            return eval(self.metric, safe_locals)
    
    def get_billing_point(self, order, bp=None, **options):
        not_cachable = self.billing_point is self.FIXED_DATE and options.get('fixed_point')
        if not_cachable or bp is None:
            bp = options.get('billing_point', timezone.now().date())
            if not options.get('fixed_point'):
                if self.billing_period is self.MONTHLY:
                    date = bp
                    if self.payment_style is self.PREPAY:
                        date += relativedelta(months=1)
                    if self.billing_point is self.ON_REGISTER:
                        day = order.registered_on.day
                    elif self.billing_point is self.FIXED_DATE:
                        day = 1
                    bp = datetime.datetime(year=date.year, month=date.month,
                            day=day, tzinfo=timezone.get_current_timezone())
                elif self.billing_period is self.ANUAL:
                    if self.billing_point is self.ON_REGISTER:
                        month = order.registered_on.month
                        day = order.registered_on.day
                    elif self.billing_point is self.FIXED_DATE:
                        month = settings.ORDERS_SERVICE_ANUAL_BILLING_MONTH
                        day = 1
                    year = bp.year
                    if self.payment_style is self.POSTPAY:
                        year = bo.year - relativedelta(years=1)
                    if bp.month >= month:
                        year = bp.year + 1
                    bp = datetime.datetime(year=year, month=month, day=day,
                        tzinfo=timezone.get_current_timezone())
                elif self.billing_period is self.NEVER:
                    bp = order.registered_on
                else:
                    raise NotImplementedError(
                        "Support for '%s' billing period and '%s' billing point is not implemented"
                        % (self.display_billing_period(), self.display_billing_point())
                    )
        if self.on_cancel is not self.NOTHING and order.cancelled_on < bp:
            return order.cancelled_on
        return bp
    
    def get_pricing_size(self, ini, end):
        rdelta = relativedelta.relativedelta(end, ini)
        if self.get_pricing_period() is self.MONTHLY:
            size = rdelta.months
            days = calendar.monthrange(bp.year, bp.month)[1]
            size += float(bp.day)/days
        elif self.get_pricint_period() is self.ANUAL:
            size = rdelta.years
            size += float(rdelta.days)/365
        elif self.get_pricing_period() is self.NEVER:
            size = 1
        else:
            raise NotImplementedError
        return size
    
    def get_pricing_slots(self, ini, end):
        period = self.get_pricing_period()
        if period is self.MONTHLY:
            rdelta = relativedelta(months=1)
        elif period is self.ANUAL:
            rdelta = relativedelta(years=1)
        elif period is self.NEVER:
            yield ini, end
            raise StopIteration
        else:
            raise NotImplementedError
        while True:
            next = ini + rdelta
            if next >= end:
                yield ini, end
                break
            yield ini, next
            ini = next
    
    def create_line(self, order, price, size):
        nominal_price = self.nominal_price * size
        if nominal_price > price:
            discount = nominal_price-price
    
    def create_bill_lines(self, orders, **options):
        # Perform compensations on cancelled services
        # TODO WTF to do with day 1 of each month.
        if self.on_cancel in (Order.COMPENSATE, Order.REFOUND):
            # TODO compensations with commit=False, fuck commit or just fuck the transaction?
            compensate(orders, **options)
            # TODO create discount per compensation
        bp = None
        lines = []
        for order in orders:
            bp = self.get_billing_point(order, bp=bp, **options)
            ini = order.billed_until or order.registered_on
            if bp < ini:
                continue
            if not self.metric:
                # Number of orders metric; bill line per order
                porders = service.orders.filter(account=order.account).filter(
                    Q(is_active=True) | Q(cancelled_on__gt=order.billed_until)
                    ).filter(registered_on__lt=bp)
                price = 0
                size = self.get_pricing_size(ini, bp)
                if self.orders_effect is self.REGISTER_OR_RENEW:
                    events = get_register_or_renew_events(porders, ini, bp)
                elif self.orders_effect is self.CONCURRENT:
                    events = get_register_or_cancel_events(porders, ini, bp)
                else:
                    raise NotImplementedError
                for metric, ratio in events:
                    price += self.get_rate(metric, account) * size * ratio
                lines += self.create_line(order, price, size)
            else:
                # weighted metric; bill line per pricing period
                for ini, end in self.get_pricing_slots(ini, bp):
                    metric = order.get_metric(ini, end)
                    size = self.get_pricing_size(ini, end)
                    price = self.get_rate(metric, account) * size
                    lines += self.create_line(order, price, size)
        return lines
    
    def compensate(self, orders):
        # num orders and weights
        # Discounts
        pass
