import calendar
import datetime
import decimal

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
                        tzinfo=timezone.get_current_timezone()).date()
                elif self.billing_period == self.ANUAL:
                    if self.billing_point == self.ON_REGISTER:
                        month = order.registered_on.month
                        day = order.registered_on.day
                    elif self.billing_point == self.FIXED_DATE:
                        month = settings.SERVICES_SERVICE_ANUAL_BILLING_MONTH
                        day = 1
                    else:
                        raise NotImplementedError(msg)
                    year = bp.year
                    if self.payment_style == self.POSTPAY:
                        year = bo.year - relativedelta.relativedelta(years=1)
                    if bp.month >= month:
                        year = bp.year + 1
                    bp = datetime.datetime(year=year, month=month, day=day,
                        tzinfo=timezone.get_current_timezone()).date()
                elif self.billing_period == self.NEVER:
                    bp = order.registered_on
                else:
                    raise NotImplementedError(msg)
        if self.on_cancel != self.NOTHING and order.cancelled_on and order.cancelled_on < bp:
            return order.cancelled_on
        return bp
    
    def get_price_size(self, ini, end):
        rdelta = relativedelta.relativedelta(end, ini)
        if self.billing_period == self.MONTHLY:
            size = rdelta.years * 12
            size += rdelta.months
            days = calendar.monthrange(end.year, end.month)[1]
            size += decimal.Decimal(rdelta.days)/days
        elif self.billing_period == self.ANUAL:
            size = rdelta.years
            size += decimal.Decimal(rdelta.months)/12
            days = 366 if calendar.isleap(end.year) else 365
            size += decimal.Decimal(rdelta.days)/days
        elif self.billing_period == self.NEVER:
            size = 1
        else:
            raise NotImplementedError
        return decimal.Decimal(size)
    
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
    
    def generate_discount(self, line, dtype, price):
        line.discounts.append(AttributeDict(**{
            'type': dtype,
            'total': price,
        }))
    
    def generate_line(self, order, price, size, ini, end, discounts=[]):
        subtotal = self.nominal_price * size
        line = AttributeDict(**{
            'order': order,
            'subtotal': subtotal,
            'size': size,
            'ini': ini,
            'end': end,
            'discounts': [],
        })
        discounted = 0
        for dtype, dprice in discounts:
            self.generate_discount(line, dtype, dprice)
            discounted += dprice
        subtotal -= discounted
        if subtotal > price:
            self.generate_discount(line, 'volume', price-subtotal)
        return line

    def compensate(self, givers, receivers, commit=True):
        compensations = []
        for order in givers:
            if order.billed_until and order.cancelled_on and order.cancelled_on < order.billed_until:
                interval = helpers.Interval(order.cancelled_on, order.billed_until, order)
                compensations.append[interval]
        for order in receivers:
            if not order.billed_until or order.billed_until < order.new_billed_until:
                # receiver
                ini = order.billed_until or order.registered_on
                end = order.cancelled_on or datetime.date.max
                order_interval = helpers.Interval(ini, order.new_billed_until)
                compensations, used_compensations = helpers.compensate(order_interval, compensations)
                order._compensations = used_compensations
                for comp in used_compensations:
                    comp.order.new_billed_until = min(comp.order.billed_until, comp.end)
        if commit:
            for order in givers:
                if hasattr(order, 'new_billed_until'):
                    order.billed_until = order.new_billed_until
                    order.save()
    
    def get_register_or_renew_events(self, porders, ini, end):
        # TODO count intermediat billing points too
        counter = 0
        for order in porders:
            bu = getattr(order, 'new_billed_until', order.billed_until)
            if bu:
                if order.register >= ini and order.register < end:
                    counter += 1
                if order.register != bu and bu >= ini and bu < end:
                    counter += 1
                if order.billed_until and order.billed_until != bu:
                    if order.register != order.billed_until and order.billed_until >= ini and order.billed_until < end:
                        counter += 1
        return counter
    
    def bill_concurrent_orders(self, account, porders, rates, ini, end, commit=True):
        # Concurrent
        # Get pricing orders
        priced = {}
        for ini, end, orders in helpers.get_chunks(porders, ini, end):
            size = self.get_price_size(ini, end)
            metric = len(orders)
            interval = helpers.Interval(ini=ini, end=end)
            for position, order in enumerate(orders):
                csize = 0
                compensations = getattr(order, '_compensations', [])
                for comp in compensations:
                    intersect = comp.intersect(interval)
                    if intersect:
                        csize += self.get_price_size(intersect.ini, intersect.end)
                price = self.get_price(account, metric, position=position, rates=rates)
                price = price * size
                cprice = price * (size-csize)
                if order in prices:
                    priced[order][0] += price
                    priced[order][1] += cprice
                else:
                    priced[order] = (price, cprice)
        lines = []
        for order, prices in priced.iteritems():
            # Generate lines and discounts from order.nominal_price
            price, cprice = prices
            if cprice:
                discounts = (('compensation', cprice),)
            line = self.generate_line(order, price, size, ini, end, discounts=discounts)
            lines.append(line)
            if commit:
                order.billed_until = order.new_billed_until
                order.save()
        return lines
    
    def bill_registered_or_renew_events(self, account, porders, rates, ini, end, commit=True):
        # Before registration
        lines = []
        perido = self.get_pricing_period()
        if period == self.MONTHLY:
            rdelta = relativedelta.relativedelta(months=1)
        elif period == self.ANUAL:
            rdelta = relativedelta.relativedelta(years=1)
        elif period == self.NEVER:
            raise NotImplementedError("Rates with no pricing period?")
        ini -= rdelta
        for position, order in enumerate(porders):
            if hasattr(order, 'new_billed_until'):
                cend = order.billed_until or order.registered_on
                cini = cend - rdelta
                metric = self.get_register_or_renew_events(porders, cini, cend)
                size = self.get_price_size(ini, end)
                price = self.get_price(account, metric, position=position, rates=rates)
                price = price * size
                line = self.generate_line(order, price, size, ini, end)
                lines.append(line)
                if commit:
                    order.billed_until = order.new_billed_until
                    order.save()
    
    def bill_with_orders(self, orders, account, **options):
        # For the "boundary conditions" just think that:
        #   date(2011, 1, 1) is equivalent to datetime(2011, 1, 1, 0, 0, 0)
        #   In most cases:
        #       ini >= registered_date, end < registered_date
        bp = None
        lines = []
        commit = options.get('commit', True)
        ini = datetime.date.max
        end = datetime.date.min
        # boundary lookup
        for order in orders:
            cini = order.registered_on
            if order.billed_until:
                cini = order.billed_until
            bp = self.get_billing_point(order, bp=bp, **options)
            order.new_billed_until = bp
            ini = min(ini, cini)
            end = max(end, bp)
        related_orders = account.orders.filter(service=self.service)
        if self.on_cancel == self.COMPENSATE:
            # Get orders pending for compensation
            givers = related_orders.filter_givers(ini, end)
            givers.sort(cmp=helpers.cmp_billed_until_or_registered_on)
            orders.sort(cmp=helpers.cmp_billed_until_or_registered_on)
            self.compensate(givers, orders, commit=commit)
        
        rates = self.get_rates(account)
        if rates:
            porders = related_orders.filter_pricing_orders(ini, end)
            porders = list(set(orders).union(set(porders)))
            porders.sort(cmp=helpers.cmp_billed_until_or_registered_on)
            if self.billing_period != self.NEVER and self.get_pricing_period != self.NEVER:
                liens = self.bill_concurrent_orders(account, porders, rates, ini, end, commit=commit)
            else:
                lines = self.bill_registered_or_renew_events(account, porders, rates, ini, end, commit=commit)
        else:
            lines = []
            price = self.nominal_price
            # Calculate nominal price
            for order in orders:
                ini = order.billed_until or order.registered_on
                end = order.new_billed_until
                size = self.get_price_size(ini, end)
                order.nominal_price = price * size
                line = self.generate_line(order, price*size, size, ini, end)
                lines.append(line)
                if commit:
                    order.billed_until = order.new_billed_until
                    order.save()
        return lines
    
    def bill_with_metric(self, orders, account, **options):
        lines = []
        commit = options.get('commit', True)
        for order in orders:
            bp = self.get_billing_point(order, bp=bp, **options)
            ini = order.billed_until or order.registered_on
            if bp <= ini:
                continue
            order.new_billed_until = bp
            # weighted metric; bill line per pricing period
            prev = None
            lines_info = []
            for ini, end in self.get_pricing_slots(ini, bp):
                size = self.get_price_size(ini, end)
                metric = order.get_metric(ini, end)
                price = self.get_price(order, metric)
                current = AttributeDict(price=price, size=size, ini=ini, end=end)
                if prev and prev.metric == current.metric and prev.end == current.end:
                    prev.end = current.end
                    prev.size += current.size
                    prev.price += current.price
                else:
                    lines_info.append(current)
                prev = current
            for line in lines_info:
                lines.append(self.generate_line(order, price, size, ini, end))
            if commit:
                order.billed_until = order.new_billed_until
                order.save()
        return lines
    
    def generate_bill_lines(self, orders, account, **options):
        if not self.metric:
            lines = self.bill_with_orders(orders, account, **options)
        else:
            lines = self.bill_with_metric(orders, account, **options)
        return lines
