import calendar
import datetime

from dateutil import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.utils import plugins
from orchestra.utils.python import AttributeDict

from . import settings, helpers


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
        not_cachable = self.billing_point == self.FIXED_DATE and options.get('fixed_point')
        if not_cachable or bp is None:
            bp = options.get('billing_point', timezone.now().date())
            if not options.get('fixed_point'):
                msg = ("Support for '%s' period and '%s' point is not implemented"
                    % (self.get_billing_period_display(), self.get_billing_point_display()))
                if self.billing_period == self.MONTHLY:
                    date = bp
                    if self.payment_style == self.PREPAY:
                        date += relativedelta.relativedelta(months=1)
                    if self.billing_point == self.ON_REGISTER:
                        day = order.registered_on.day
                    elif self.billing_point == self.FIXED_DATE:
                        day = 1
                    else:
                        raise NotImplementedError(msg)
                    bp = datetime.datetime(year=date.year, month=date.month, day=day,
                        tzinfo=timezone.get_current_timezone())
                elif self.billing_period == self.ANUAL:
                    if self.billing_point == self.ON_REGISTER:
                        month = order.registered_on.month
                        day = order.registered_on.day
                    elif self.billing_point == self.FIXED_DATE:
                        month = settings.ORDERS_SERVICE_ANUAL_BILLING_MONTH
                        day = 1
                    else:
                        raise NotImplementedError(msg)
                    year = bp.year
                    if self.payment_style == self.POSTPAY:
                        year = bo.year - relativedelta.relativedelta(years=1)
                    if bp.month >= month:
                        year = bp.year + 1
                    bp = datetime.datetime(year=year, month=month, day=day,
                        tzinfo=timezone.get_current_timezone())
                elif self.billing_period == self.NEVER:
                    bp = order.registered_on
                else:
                    raise NotImplementedError(msg)
        if self.on_cancel != self.NOTHING and order.cancelled_on and order.cancelled_on < bp:
            return order.cancelled_on
        return bp
    
    def get_pricing_size(self, ini, end):
        rdelta = relativedelta.relativedelta(end, ini)
        if self.get_pricing_period() == self.MONTHLY:
            size = rdelta.months
            days = calendar.monthrange(end.year, end.month)[1]
            size += float(rdelta.days)/days
        elif self.get_pricing_period() == self.ANUAL:
            size = rdelta.years
            days = 366 if calendar.isleap(end.year) else 365
            size += float((end-ini).days)/days
        elif self.get_pricing_period() == self.NEVER:
            size = 1
        else:
            raise NotImplementedError
        return size
    
    def get_pricing_slots(self, ini, end):
        period = self.get_pricing_period()
        if period == self.MONTHLY:
            rdelta = relativedelta.relativedelta(months=1)
        elif period == self.ANUAL:
            rdelta = relativedelta.relativedelta(years=1)
        elif period == self.NEVER:
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
    
    def get_price_with_orders(self, order, size, ini, end):
        porders = self.orders.filter(account=order.account).filter(
            Q(cancelled_on__isnull=True) | Q(cancelled_on__gt=ini)
            ).filter(registered_on__lt=end).order_by('registered_on')
        price = 0
        if self.orders_effect == self.REGISTER_OR_RENEW:
            events = helpers.get_register_or_renew_events(porders, order, ini, end)
        elif self.orders_effect == self.CONCURRENT:
            events = helpers.get_register_or_cancel_events(porders, order, ini, end)
        else:
            raise NotImplementedError
        for metric, position, ratio in events:
            price += self.get_price(order, metric, position=position) * size * ratio
        return price
    
    def get_price_with_metric(self, order, size, ini, end):
        metric = order.get_metric(ini, end)
        price = self.get_price(order, metric) * size
        return price
    
    def generate_line(self, order, price, size, ini, end):
        subtotal = float(self.nominal_price) * size
        discounts = []
        if subtotal > price:
            discounts.append(AttributeDict(**{
                'type': 'volume',
                'total': price-subtotal
            }))
        elif subtotal < price:
            raise ValueError("Something is wrong!")
        return AttributeDict(**{
            'order': order,
            'subtotal': subtotal,
            'size': size,
            'ini': ini,
            'end': end,
            'discounts': discounts,
        })
    
    def _generate_bill_lines(self, orders, account, **options):
        # For the "boundary conditions" just think that:
        #   date(2011, 1, 1) is equivalent to datetime(2011, 1, 1, 0, 0, 0)
        #   In most cases:
        #       ini >= registered_date, end < registered_date
        
        bp = None
        lines = []
        commit = options.get('commit', True)
        ini = datetime.date.max
        end = datetime.date.ini
        # boundary lookup
        for order in orders:
            cini = order.registered_on
            if order.billed_until:
                cini = order.billed_until
            bp = self.get_billing_point(order, bp=bp, **options)
            order.new_billed_until = bp
            ini = min(ini, cini)
            end = max(end, bp) # TODO if all bp are the same ...
        
        related_orders = Order.objects.filter(service=self.service, account=account)
        if self.on_cancel == self.COMPENSATE:
            # Get orders pending for compensation
            givers = related_orders.filter_givers(ini, end)
            givers.sort(cmp=helpers.cmp_billed_until_or_registered_on)
            orders.sort(cmp=helpers.cmp_billed_until_or_registered_on)
            self.compensate(givers, orders)
        
        rates = 'TODO'
        if rates:
            # Get pricing orders
            porders = related_orders.filter_pricing_orders(ini, end)
            porders = set(orders).union(set(porders))
            for ini, end, orders in self.get_chunks(porders, ini, end):
                if self.pricing_period == self.ANUAL:
                    pass
                elif self.pricing_period == self.MONTHLY:
                    pass
                else:
                    raise NotImplementedError
                metric = len(orders)
                for position, order in enumerate(orders):
                    # TODO position +1?
                    price = self.get_price(order, metric, position=position)
                    price *= size
        else:
            pass
    
    def compensate(self, givers, receivers):
        compensations = []
        for order in givers:
            if order.billed_until and order.cancelled_on and order.cancelled_on < order.billed_until:
                compensations.append[Interval(order.cancelled_on, order.billed_until, order)]
        for order in receivers:
            if not order.billed_until or order.billed_until < order.new_billed_until:
                # receiver
                ini = order.billed_until or order.registered_on
                end = order.cancelled_on or datetime.date.max
                order_interval = helpers.Interval(ini, order.new_billed_until) # TODO beyond interval?
                compensations, used_compensations = helpers.compensate(order_interval, compensations)
                order._compensations = used_compensations
                for comp in used_compensations:
                    comp.order.billed_until = min(comp.order.billed_until, comp.end)
    
    def get_chunks(self, porders, ini, end, ix=0):
        if ix >= len(porders):
            return [[ini, end, []]]
        order = porders[ix]
        ix += 1
        bu = getattr(order, 'new_billed_until', order.billed_until)
        if not bu or bu <= ini or order.registered_on >= end:
            return self.get_chunks(porders, ini, end, ix=ix)
        result = []
        if order.registered_on < end and order.registered_on > ini:
            ro = order.registered_on
            result = self.get_chunks(porders, ini, ro, ix=ix)
            ini = ro
        if bu < end:
            result += self.get_chunks(porders, bu, end, ix=ix)
            end = bu
        chunks = self.get_chunks(porders, ini, end, ix=ix)
        for chunk in chunks:
            chunk[2].insert(0, order)
            result.append(chunk)
        return result
    
    def generate_bill_lines(self, orders, **options):
        # For the "boundary conditions" just think that:
        #   date(2011, 1, 1) is equivalent to datetime(2011, 1, 1, 0, 0, 0)
        #   In most cases:
        #       ini >= registered_date, end < registered_date
        
        # TODO Perform compensations on cancelled services
        if self.on_cancel in (self.COMPENSATE, self.REFOUND):
            pass
            # TODO compensations with commit=False, fuck commit or just fuck the transaction?
            # compensate(orders, **options)
            # TODO create discount per compensation
        bp = None
        lines = []
        commit = options.get('commit', True)
        for order in orders:
            bp = self.get_billing_point(order, bp=bp, **options)
            ini = order.billed_until or order.registered_on
            if bp <= ini:
                continue
            if not self.metric:
                # Number of orders metric; bill line per order
                size = self.get_pricing_size(ini, bp)
                price = self.get_price_with_orders(order, size, ini, bp)
                lines.append(self.generate_line(order, price, size, ini, bp))
            else:
                # weighted metric; bill line per pricing period
                for ini, end in self.get_pricing_slots(ini, bp):
                    size = self.get_pricing_size(ini, end)
                    price = self.get_price_with_metric(order, size, ini, end)
                    lines.append(self.generate_line(order, price, size, ini, end))
            order.billed_until = bp
            if commit:
                order.save()
        return lines
