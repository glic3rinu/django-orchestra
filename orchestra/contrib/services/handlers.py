import calendar
import datetime
import decimal
import math
from functools import cmp_to_key

from dateutil import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils import timezone, translation
from django.utils.translation import ugettext, ugettext_lazy as _

from orchestra import plugins
from orchestra.utils.humanize import text2int
from orchestra.utils.python import AttrDict, format_exception

from . import settings, helpers


class ServiceHandler(plugins.Plugin, metaclass=plugins.PluginMount):
    """
    Separates all the logic of billing handling from the model allowing to better
    customize its behaviout
    
    Relax and enjoy the journey.
    """
    _PLAN = 'plan'
    _COMPENSATION = 'compensation'
    _PREPAY = 'prepay'
    
    model = None
    
    def __init__(self, service):
        self.service = service
    
    def __getattr__(self, attr):
        return getattr(self.service, attr)
    
    @classmethod
    def get_choices(cls):
        choices = super(ServiceHandler, cls).get_choices()
        return [('', _("Default"))] + choices
    
    def validate_content_type(self, service):
        pass
    
    def validate_expression(self, service, method):
        try:
            obj = service.content_type.model_class().objects.all()[0]
        except IndexError:
            return
        try:
            bool(getattr(self, method)(obj))
        except Exception as exc:
            raise ValidationError(format_exception(exc))
    
    def validate_match(self, service):
        if not service.match:
            service.match = 'True'
        self.validate_expression(service, 'matches')
    
    def validate_metric(self, service):
        self.validate_expression(service, 'get_metric')
    
    def validate_order_description(self, service):
        self.validate_expression(service, 'get_order_description')
    
    def get_content_type(self):
        if not self.model:
            return self.content_type
        app_label, model = self.model.split('.')
        return ContentType.objects.get_by_natural_key(app_label, model.lower())
    
    def get_expression_context(self, instance):
        return {
            'instance': instance,
            'obj': instance,
            'ugettext': ugettext,
            'handler': self,
            'service': self.service,
            instance._meta.model_name: instance,
            'math': math,
            'logsteps': lambda n, size=1: \
                round(n/(decimal.Decimal(size*10**int(math.log10(max(n, 1))))))*size*10**int(math.log10(max(n, 1))),
            'log10': math.log10,
            'Decimal': decimal.Decimal,
        }
    
    def matches(self, instance):
        if not self.match:
            # Blank expressions always evaluate True
            return True
        safe_locals = self.get_expression_context(instance)
        return eval(self.match, safe_locals)
    
    def get_ignore_delta(self):
        if self.ignore_period == self.NEVER:
            return None
        value, unit = self.ignore_period.split('_')
        value = text2int(value)
        if unit.lower().startswith('day'):
            return datetime.timedelta(days=value)
        if unit.lower().startswith('month'):
            return datetime.timedelta(months=value)
        else:
            raise ValueError("Unknown unit %s" % unit)
    
    def get_order_ignore(self, order):
        """ service trial delta """
        ignore_delta = self.get_ignore_delta()
        if ignore_delta and (order.cancelled_on-ignore_delta).date() <= order.registered_on:
            return True
        return order.ignore
    
    def get_ignore(self, instance):
        if self.ignore_superusers:
            account = getattr(instance, 'account', instance)
            if account.type in settings.SERVICES_IGNORE_ACCOUNT_TYPE:
                return True
            if 'superuser' in settings.SERVICES_IGNORE_ACCOUNT_TYPE and account.is_superuser:
                return True
        return False
    
    def get_metric(self, instance):
        if self.metric:
            safe_locals = self.get_expression_context(instance)
            try:
                return eval(self.metric, safe_locals)
            except Exception as exc:
                raise type(exc)("'%s' evaluating metric for '%s' service" % (exc, self.service))
    
    def get_order_description(self, instance):
        safe_locals = self.get_expression_context(instance)
        account = getattr(instance, 'account', instance)
        with translation.override(account.language):
            if not self.order_description:
                return '%s: %s' % (ugettext(self.description), instance)
            return eval(self.order_description, safe_locals)
    
    def get_billing_point(self, order, bp=None, **options):
        cachable = bool(self.billing_point == self.FIXED_DATE and not options.get('fixed_point'))
        if not cachable or bp is None:
            bp = options.get('billing_point') or timezone.now().date()
            if not options.get('fixed_point'):
                msg = ("Support for '%s' period and '%s' point is not implemented"
                    % (self.get_billing_period_display(), self.get_billing_point_display()))
                if self.billing_period == self.MONTHLY:
                    date = bp
                    if self.payment_style == self.PREPAY:
                        date += relativedelta.relativedelta(months=1)
                    else:
                        date = timezone.now().date()
                    if self.billing_point == self.ON_REGISTER:
                        day = order.registered_on.day
                    elif self.billing_point == self.FIXED_DATE:
                        day = 1
                    else:
                        raise NotImplementedError(msg)
                    bp = datetime.date(year=date.year, month=date.month, day=day)
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
                        year = bp.year - relativedelta.relativedelta(years=1)
                    if bp.month >= month:
                        year = bp.year + 1
                    bp = datetime.date(year=year, month=month, day=day)
                elif self.billing_period == self.NEVER:
                    bp = order.registered_on
                else:
                    raise NotImplementedError(msg)
        if self.on_cancel != self.NOTHING and order.cancelled_on and order.cancelled_on < bp:
            bp = order.cancelled_on
        return bp
    
#    def aligned(self, date):
#        if self.granularity == self.DAILY:
#            return date
#        elif self.granularity == self.MONTHLY:
#            return datetime.date(year=date.year, month=date.month, day=1)
#        elif self.granularity == self.ANUAL:
#            return datetime.date(year=date.year, month=1, day=1)
#        raise NotImplementedError
    
    def get_price_size(self, ini, end):
        rdelta = relativedelta.relativedelta(end, ini)
        anual_prepay_of_monthly_pricing = bool(
            self.billing_period == self.ANUAL and
            self.payment_style == self.PREPAY and
            self.get_pricing_period() == self.MONTHLY)
        if self.billing_period == self.MONTHLY or anual_prepay_of_monthly_pricing:
            size = rdelta.years * 12
            size += rdelta.months
            days = calendar.monthrange(end.year, end.month)[1]
            size += decimal.Decimal(str(rdelta.days))/days
        elif self.billing_period == self.ANUAL:
            size = rdelta.years
            size += decimal.Decimal(str(rdelta.months))/12
            days = 366 if calendar.isleap(end.year) else 365
            size += decimal.Decimal(str(rdelta.days))/days
        elif self.billing_period == self.NEVER:
            size = 1
        else:
            raise NotImplementedError
        size = round(size, 2)
        return decimal.Decimal(str(size))
    
    def get_pricing_slots(self, ini, end):
        day = 1
        month = settings.SERVICES_SERVICE_ANUAL_BILLING_MONTH
        if self.billing_point == self.ON_REGISTER:
            day = ini.day
            month = ini.month
        period = self.get_pricing_period()
        rdelta = self.get_pricing_rdelta()
        if period == self.MONTHLY:
            ini = datetime.date(year=ini.year, month=ini.month, day=day)
        elif period == self.ANUAL:
            ini = datetime.date(year=ini.year, month=month, day=day)
        elif period == self.NEVER:
            yield ini, end
            raise StopIteration
        else:
            raise NotImplementedError
        while True:
            next = ini + rdelta
            yield ini, next
            if next >= end:
                break
            ini = next
    
    def get_pricing_rdelta(self):
        period = self.get_pricing_period()
        if period == self.MONTHLY:
            return relativedelta.relativedelta(months=1)
        elif period == self.ANUAL:
            return relativedelta.relativedelta(years=1)
        elif period == self.NEVER:
            return None
    
    def generate_discount(self, line, dtype, price):
        line.discounts.append(AttrDict(**{
            'type': dtype,
            'total': price,
        }))
    
    def generate_line(self, order, price, *dates, metric=1, discounts=None, computed=False):
        """
        discounts: extra discounts to apply
        computed: price = price*size already performed
        """
        if len(dates) == 2:
            ini, end = dates
        elif len(dates) == 1:
            ini, end = dates[0], dates[0]
        else:
            raise AttributeError("WTF is '%s'?" % dates)
        discounts = discounts or ()
        
        size = self.get_price_size(ini, end)
        if not computed:
            price = price * size
        subtotal = self.nominal_price * size * metric
        line = AttrDict(**{
            'order': order,
            'subtotal': subtotal,
            'ini': ini,
            'end': end,
            'size': size,
            'metric': metric,
            'discounts': [],
        })
        
        if subtotal > price:
            plan_discount = price-subtotal
            self.generate_discount(line, self._PLAN, plan_discount)
            subtotal += plan_discount
        for dtype, dprice in discounts:
            subtotal += dprice
            # Prevent compensations/prepays to refund money
            if dtype in (self._COMPENSATION, self._PREPAY) and subtotal < 0:
                dprice -= subtotal
            if dprice:
                self.generate_discount(line, dtype, dprice)
        return line
    
    def assign_compensations(self, givers, receivers, **options):
        compensations = []
        for order in givers:
            if order.billed_until and order.cancelled_on and order.cancelled_on < order.billed_until:
                interval = helpers.Interval(order.cancelled_on, order.billed_until, order)
                compensations.append(interval)
        for order in receivers:
            if not order.billed_until or order.billed_until < order.new_billed_until:
                # receiver
                ini = order.billed_until or order.registered_on
                end = order.cancelled_on or datetime.date.max
                interval = helpers.Interval(ini, end)
                compensations, used_compensations = helpers.compensate(interval, compensations)
                order._compensations = used_compensations
                for comp in used_compensations:
                    comp.order.new_billed_until = min(comp.order.billed_until, comp.ini,
                            getattr(comp.order, 'new_billed_until', datetime.date.max))
        if options.get('commit', True):
            for order in givers:
                if hasattr(order, 'new_billed_until'):
                    order.billed_until = order.new_billed_until
                    order.save(update_fields=['billed_until'])
    
    def apply_compensations(self, order, only_beyond=False):
        dsize = 0
        ini = order.billed_until or order.registered_on
        end = order.new_billed_until
        beyond = end
        cend = None
        new_end = None
        for comp in getattr(order, '_compensations', []):
            intersect = comp.intersect(helpers.Interval(ini=ini, end=end))
            if intersect:
                cini, cend = intersect.ini, intersect.end
                if comp.end > beyond:
                    cend = comp.end
                    new_end = cend
                    if only_beyond:
                        cini = beyond
                elif only_beyond:
                    continue
                dsize += self.get_price_size(cini, cend)
            # Extend billing point a little bit to benefit from a substantial discount
            elif comp.end > beyond and (comp.end-comp.ini).days > 3*(comp.ini-beyond).days:
                cend = comp.end
                new_end = cend
                dsize += self.get_price_size(comp.ini, cend)
        return dsize, new_end
    
    def get_register_or_renew_events(self, porders, ini, end):
        counter = 0
        for order in porders:
            bu = getattr(order, 'new_billed_until', order.billed_until)
            if bu:
                registered = order.registered_on
                if registered > ini and registered <= end:
                    counter += 1
                if registered != bu and bu > ini and bu <= end:
                    counter += 1
                if order.billed_until and order.billed_until != bu:
                    if registered != order.billed_until and order.billed_until > ini and order.billed_until <= end:
                        counter += 1
        return counter
    
    def bill_concurrent_orders(self, account, porders, rates, ini, end):
        # Concurrent
        # Get pricing orders
        priced = {}
        for ini, end, orders in helpers.get_chunks(porders, ini, end):
            size = self.get_price_size(ini, end)
            metric = len(orders)
            interval = helpers.Interval(ini=ini, end=end)
            for position, order in enumerate(orders, start=1):
                csize = 0
                compensations = getattr(order, '_compensations', [])
                # Compensations < new_billed_until
                for comp in compensations:
                    intersect = comp.intersect(interval)
                    if intersect:
                        csize += self.get_price_size(intersect.ini, intersect.end)
                price = self.get_price(account, metric, position=position, rates=rates)
                cprice = price * csize
                price = price * size
                if order in priced:
                    priced[order][0] += price
                    priced[order][1] += cprice
                else:
                    priced[order] = [price, cprice]
        lines = []
        for order, prices in priced.items():
            if hasattr(order, 'new_billed_until'):
                discounts = ()
                # Generate lines and discounts from order.nominal_price
                price, cprice = prices
                a = order.id
                # Compensations > new_billed_until
                dsize, new_end = self.apply_compensations(order, only_beyond=True)
                cprice += dsize*price
                if cprice:
                    discounts = (
                        (self._COMPENSATION, -cprice),
                    )
                    if new_end:
                        size = self.get_price_size(order.new_billed_until, new_end)
                        price += price*size
                        order.new_billed_until = new_end
                ini = order.billed_until or order.registered_on
                end = new_end or order.new_billed_until
                line = self.generate_line(
                    order, price, ini, end, discounts=discounts, computed=True)
                lines.append(line)
        return lines
    
    def bill_registered_or_renew_events(self, account, porders, rates):
        # Before registration
        lines = []
        rdelta = self.get_pricing_rdelta()
        if not rdelta:
            raise NotImplementedError
        for position, order in enumerate(porders, start=1):
            if hasattr(order, 'new_billed_until'):
                pend = order.billed_until or order.registered_on
                pini = pend - rdelta
                metric = self.get_register_or_renew_events(porders, pini, pend)
                position = min(position, metric)
                price = self.get_price(account, metric, position=position, rates=rates)
                ini = order.billed_until or order.registered_on
                end = order.new_billed_until
                discounts = ()
                dsize, new_end = self.apply_compensations(order)
                if dsize:
                    discounts=(
                        (self._COMPENSATION, -dsize*price),
                    )
                    if new_end:
                        order.new_billed_until = new_end
                        end = new_end
                line = self.generate_line(order, price, ini, end, discounts=discounts)
                lines.append(line)
        return lines
    
    def bill_with_orders(self, orders, account, **options):
        # For the "boundary conditions" just think that:
        #   date(2011, 1, 1) is equivalent to datetime(2011, 1, 1, 0, 0, 0)
        #   In most cases:
        #       ini >= registered_date, end < registered_date
        # boundary lookup and exclude cancelled and billed
        orders_ = []
        bp = None
        ini = datetime.date.max
        end = datetime.date.min
        for order in orders:
            cini = order.registered_on
            if order.billed_until:
                # exclude cancelled and billed
                if self.on_cancel != self.REFUND:
                    if order.cancelled_on and order.billed_until > order.cancelled_on:
                        continue
                cini = order.billed_until
            bp = self.get_billing_point(order, bp=bp, **options)
            if order.billed_until and order.billed_until >= bp:
                continue
            order.new_billed_until = bp
            ini = min(ini, cini)
            end = max(end, bp)
            orders_.append(order)
        orders = orders_
        
        # Compensation
        related_orders = account.orders.filter(service=self.service)
        if self.payment_style == self.PREPAY and self.on_cancel == self.COMPENSATE:
            # Get orders pending for compensation
            givers = list(related_orders.givers(ini, end))
            givers = sorted(givers, key=cmp_to_key(helpers.cmp_billed_until_or_registered_on))
            orders = sorted(orders, key=cmp_to_key(helpers.cmp_billed_until_or_registered_on))
            self.assign_compensations(givers, orders, **options)
        rates = self.get_rates(account)
        has_billing_period = self.billing_period != self.NEVER
        has_pricing_period = self.get_pricing_period() != self.NEVER
        if rates and (has_billing_period or has_pricing_period):
            concurrent = has_billing_period and not has_pricing_period
            if not concurrent:
                rdelta = self.get_pricing_rdelta()
                ini -= rdelta
            porders = related_orders.pricing_orders(ini, end)
            porders = list(set(orders).union(set(porders)))
            porders = sorted(porders, key=cmp_to_key(helpers.cmp_billed_until_or_registered_on))
            if concurrent:
                # Periodic billing with no pricing period
                lines = self.bill_concurrent_orders(account, porders, rates, ini, end)
            else:
                # Periodic and one-time billing with pricing period
                lines = self.bill_registered_or_renew_events(account, porders, rates)
        else:
            # No rates optimization or one-time billing without pricing period
            lines = []
            price = self.nominal_price
            # Calculate nominal price
            for order in orders:
                ini = order.billed_until or order.registered_on
                end = order.new_billed_until
                discounts = ()
                dsize, new_end = self.apply_compensations(order)
                if dsize:
                    discounts=(
                        (self._COMPENSATION, -dsize*price),
                    )
                    if new_end:
                        order.new_billed_until = new_end
                        end = new_end
                line = self.generate_line(order, price, ini, end, discounts=discounts)
                lines.append(line)
        return lines
    
    def bill_with_metric(self, orders, account, **options):
        lines = []
        bp = None
        for order in orders:
            prepay_discount = 0
            bp = self.get_billing_point(order, bp=bp, **options)
            recharged_until = datetime.date.min
            
            if (self.billing_period != self.NEVER and
                self.get_pricing_period() == self.NEVER and
                self.payment_style == self.PREPAY and order.billed_on):
                    # Recharge
                    if self.payment_style == self.PREPAY and order.billed_on:
                        recharges = []
                        rini = order.billed_on
                        rend = min(bp, order.billed_until)
                        bmetric = order.billed_metric
                        if bmetric is None:
                            bmetric = order.get_metric(order.billed_on)
                        bsize = self.get_price_size(rini, order.billed_until)
                        prepay_discount = self.get_price(account, bmetric) * bsize
                        prepay_discount = round(prepay_discount, 2)
                        for cini, cend, metric in order.get_metric(rini, rend, changes=True):
                            size = self.get_price_size(cini, cend)
                            price = self.get_price(account, metric) * size
                            discounts = ()
                            discount = min(price, max(prepay_discount, 0))
                            prepay_discount -= price
                            if discount > 0:
                                price -= discount
                                discounts = (
                                    (self._PREPAY, -discount),
                                )
                            # Don't overdload bills with lots of lines
                            if price > 0:
                                recharges.append((order, price, cini, cend, metric, discounts))
                        if prepay_discount < 0:
                            # User has prepaid less than the actual consumption
                            for order, price, cini, cend, metric, discounts in recharges:
                                if discounts:
                                    price -= discounts[0][1]
                                line = self.generate_line(order, price, cini, cend, metric=metric,
                                    computed=True, discounts=discounts)
                                lines.append(line)
                            recharged_until = cend
            if order.billed_until and order.cancelled_on and order.cancelled_on >= order.billed_until:
                # Cancelled order
                continue
            if self.billing_period != self.NEVER:
                ini = order.billed_until or order.registered_on
#                ini = max(order.billed_until or order.registered_on, recharged_until)
                # Periodic billing
                if bp <= ini:
                    # Already billed
                    continue
                order.new_billed_until = bp
                if self.get_pricing_period() == self.NEVER:
                    # Changes (Mailbox disk-like)
                    for cini, cend, metric in order.get_metric(ini, bp, changes=True):
                        cini = max(recharged_until, cini)
                        price = self.get_price(account, metric)
                        discounts = ()
                        # Since the current datamodel can't guarantee to retrieve the exact
                        # state for calculating prepay_discount (service price could have change)
                        # maybe is it better not to discount anything.
#                        discount = min(price, max(prepay_discount, 0))
#                        if discount > 0:
#                            price -= discount
#                            prepay_discount -= discount
#                            discounts = (
#                                (self._PREPAY, -discount),
#                            )
                        if metric > 0:
                            line = self.generate_line(order, price, cini, cend, metric=metric,
                                discounts=discounts)
                            lines.append(line)
                elif self.get_pricing_period() == self.billing_period:
                    # pricing_slots (Traffic-like)
                    if self.payment_style == self.PREPAY:
                        raise NotImplementedError(
                            "Metric with prepay and pricing_period == billing_period")
                    for cini, cend in self.get_pricing_slots(ini, bp):
                        metric = order.get_metric(cini, cend)
                        price = self.get_price(account, metric)
                        discounts = ()
#                        discount = min(price, max(prepay_discount, 0))
#                        if discount > 0:
#                            price -= discount
#                            prepay_discount -= discount
#                            discounts = (
#                                (self._PREPAY, -discount),
#                            )
                        if metric > 0:
                            line = self.generate_line(order, price, cini, cend, metric=metric,
                                discounts=discounts)
                            lines.append(line)
                elif self.get_pricing_period() in (self.MONTHLY, self.ANUAL):
                    if self.payment_style == self.PREPAY:
                        # Traffic Prepay
                        metric = order.get_metric(timezone.now().date())
                        if metric > 0:
                            price = self.get_price(account, metric)
                            for cini, cend in self.get_pricing_slots(ini, bp):
                                line = self.generate_line(order, price, cini, cend, metric=metric)
                                lines.append(line)
                    else:
                        raise NotImplementedError(
                            "Metric with postpay and pricing_period in (monthly, anual)")
                else:
                    raise NotImplementedError
            else:
                # One-time billing
                if order.billed_until:
                    continue
                date = timezone.now().date()
                order.new_billed_until = date
                if self.get_pricing_period() == self.NEVER:
                    # get metric (Job-like)
                    metric = order.get_metric(date)
                    price = self.get_price(account, metric)
                    line = self.generate_line(order, price, date, metric=metric)
                    lines.append(line)
                else:
                    raise NotImplementedError
            # Last processed metric for futrue recharges
            order.new_billed_metric = metric
        return lines
    
    def generate_bill_lines(self, orders, account, **options):
        if options.get('proforma', False):
            options['commit'] = False
        if not self.metric:
            lines = self.bill_with_orders(orders, account, **options)
        else:
            lines = self.bill_with_metric(orders, account, **options)
        if options.get('commit', True):
            now = timezone.now().date()
            for line in lines:
                order = line.order
                order.billed_on = now
                order.billed_metric = getattr(order, 'new_billed_metric', order.billed_metric)
                order.billed_until = getattr(order, 'new_billed_until', order.billed_until)
                order.save(update_fields=('billed_on', 'billed_until', 'billed_metric'))
        return lines
