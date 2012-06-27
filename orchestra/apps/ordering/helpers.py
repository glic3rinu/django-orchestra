from backends.billing import create_bill_line, create_bills, get_invoice_lines
from common.utils.models import group_by
from datetime import datetime
import decimal
from django.db.models import Q, F
from heapq import merge
from itertools import chain
from utils import DateTime_conv, Period


@classmethod
def get_rates(cls, service, packs, metric):
    """ Return list of rates: {'number', 'price'} for service and packs that fits with metric """


def conservative_pricing(rates, metric):

    def conservative_pricing_rec(indexes, packs, current, left, total):
        if left == 0: return [total, current]
        else: 
            results = []
            for i in range(len(packs)):
                call_indexes = list(indexes)
                call_indexes[i] += 1
                num = packs[i][indexes[i]]['number']
                price = packs[i][indexes[i]]['price']
                num = min(num, left)
                call_total = total + num * price
                call_current = list(current)
                call_current.append({'number':num, 'price':price})
                call_left = left - num
                results.append(conservative_pricing_rec(call_indexes, packs, call_current, call_left, call_total))
            minimum = results[0][0]
            result_minimum = results[0]
            for result in results:
                if result[0] < minimum:
                    minimum = result[0]
                    result_minimum = list(result)
            return result_minimum

    ix = 0
    a_rates = []
    num = rates.count()

    packs = []
    while ix < num:
        if ix+1 == num or rates[ix].pack != rates[ix+1].pack:
            number = metric
            a_rate = { 'number': number,
                       'price': rates[ix].price }
            a_rates.append(a_rate)
            packs.append(a_rates)
            a_rates = []
        else: 
            number = rates[ix+1].metric - rates[ix].metric
            a_rate = { 'number': number,
                       'price': rates[ix].price }
            a_rates.append(a_rate)
        ix += 1

    indexes = [ 0 for i in range(len(packs)) ]
    return conservative_pricing_rec(indexes, packs, [], metric, 0)[1]


def best_pricing(rates, metric):

    ix = 0
    a_rates = []
    num = rates.count()
    
    while ix < num:
        if ix+1 == num or rates[ix].pack != rates[ix+1].pack:
            number = metric
        else: number = rates[ix+1].metric - rates[ix].metric
        a_rate = { 'number': number,
                   'price': rates[ix].price }
        a_rates.append(a_rate)
        ix += 1

    a_rates = sorted(a_rates, key=lambda a_rates: a_rates['price'])            

    acumulated = 0
    f_rates = []
        
    for rate in a_rates:
        ant_acumulated = acumulated
        acumulated += rate['number']
        if acumulated >= metric: 
            rate['number'] = metric - ant_acumulated
            f_rates.append(rate)                          
            return f_rates
        f_rates.append(rate)   


def get_previous(period):
    """ Return the end date of anterior period from now()"""
    ant = datetime.now() - period
    return split_period(period, ant, ant)['final']               


def get_actual(period):
    """ Return the end date of actual period """ 
    return split_period(period, datetime.now(), datetime.now())['final']       


def get_billing_dependencies(orders, exclude=None, point=datetime.now(), fixed_point=False, force_next=False):
    """ return the orders and their deps encoded in a dict structure {'order_dep': [order_deps]} """
    deps = {}        
    Order = orders[0].__class__
    for order in list(chain(orders.metric_with_orders(), 
                            orders.metric_with_weight().weight_with_all_contact_orders())):
        qset = []
        service = order.service
        periods = order.get_pending_billing_periods(point, fixed_point, force_next)
        if not service.has_pricing_period:
            for _periods in periods.values():
                for period in _periods:
                    qset.append(period)
        else:
            if service.pricing_effect_is_current:
                for period in periods:
                    if service.pricing_is_fixed and service.billing_is_fixed:
                        qset.append(period)
                    elif not service.pricing_is_fixed and service.billing_is_fixed:
                        final = order.get_next_pricing_point(period.ini)
                        qset.append(Period(order.get_prev_pricing_point(final, lt=True), final))
                    elif service.pricing_is_fixed and not service.billing_is_fixed:
                        qset.append(Period(order.get_prev_pricing_point(period.ini), order.get_next_pricing_point(period.ini)))
                    else: qset.append(Period(order.get_prev_pricing_point(period.ini, lt=True), period.ini))
            else: 
                for _periods in periods.values():
                    for period in _periods:
                        for _period in service.split_pricing_period(period.ini, period.end):
                            qset.append(_period) 
        dep_orders = Order.objects.filter(contract__contact=order.contact, service=service)
        if service.pricing_with_weight or service.orders_with_is_active:
            dep_orders = dep_orders.billing_activity_during(qset, service)
        elif service.orders_with_is_registred:
            dep_orders = dep_orders.registred_during(qset, service)
        elif service.orders_with_is_renewed:
            dep_orders = dep_orders.renewed_during(qset, service)
        elif service.orders_with_is_registred_or_renewed:
            dep_orders = dep_orders.registred_or_renewed_during(qset, service)
        dep_orders = dep_orders.exclude(pk=order.pk)                     
        if exclude: dep_orders = dep_orders.exclude(pk__in=exclude)

        for dep_order in dep_orders:
            if not deps.has_key(dep_order): deps[dep_order]=[order]
            else: deps[dep_order].append(order)
    return deps


def _get_price(order, orders, bill_period, active_period):
    service = order.service
    if not service.has_pricing_period:
        if service.has_billing_period:
            final_price = 0                            
            if service.pricing_with_orders:
                if service.is_prepay and not service.discount_on_register and not service.discount_on_cancel:
                    a_orders = orders.billing_activity_during([bill_period], service)
                    num = 1
                    while a_orders[num-1] != order: num += 1
                    final_price = service.get_price(contact=order.contact, rating_metric=a_orders.count(), 
                        start_metric=num, end_metric=num, start_date=bill_period.ini, end_date=bill_period.end)
                elif service.is_prepay and not service.discount_on_cancel:
                    #TODO: if order is not registred yet, there is no reason to increase their price
                    a_orders = orders.billing_activity_during([Period(active_period.ini, bill_period.end)], service)
                    registers = a_orders.filter(register_date__gte=active_period.ini).values_list('register_date', flat=True)
                    changes = list(merge([active_period.ini], registers, [bill_period.end]))
                    changes.sort()
                    u_changes = [changes[0]]
                    for ix in range(len(changes)-1): 
                        if changes[ix] != changes[ix+1]: u_changes.append(changes[ix+1])     
                    changes = u_changes          
                    t_period = DateTime_conv(bill_period.end) - DateTime_conv(bill_period.ini)                         
                    for i in range(len(changes)-1):
                        c_ini = changes[i]
                        c_end = changes[i+1]
                        r_orders = a_orders.filter(register_date__lte=c_ini)
                        metric = a_orders.count()
                        num = 1
                        while r_orders[num-1] != order: num += 1
                        #Conv to mx.DateTime, because datetime is pure crap and only have 32bit outputs
                        proportion = (DateTime_conv(c_end)-DateTime_conv(c_ini)).seconds/t_period.seconds
                        proportion = decimal.Decimal(str(proportion))
                        f_price = service.get_price(contact=order.contact, 
                            rating_metric=metric, start_metric=num, end_metric=num, start_date=c_ini, end_date=c_end)
                        final_price += f_price * proportion
                else:
                    #FIXME: if_order is not active during there is no need to increase their price.
                    active_or_billed = service.orders_with_is_active_or_billed
                    if service.orders_with_is_active or active_or_billed:
                        # Mails (split into changes and price every change per occurrences)
                        if active_or_billed:
                            #TODO: move on managers
                            c_orders = orders.filter(Q(register_date__lte=active_period.end)&Q(Q(cancel_date__gte=active_period.ini)|Q(billed_until__gte=active_period.ini)))
                            registers = c_orders.filter(register_date__gte=active_period.ini).values_list('register_date', flat=True)
                            cancels = c_orders.filter(cancel_date__gt=F('billed_until')).values_list('cancel_date', flat=True)
                            billeds = c_orders.filter(cancel_date__lt=F('billed_until')).values_list('billed_until', flat=True)
                            cancel = list(merge(cancel, billed))
                        else: #Active
                            c_orders = orders.billing_activity_during([active_period], service)
                            registers = c_orders.filter(register_date__gt=active_period.ini).values_list('register_date', flat=True)
                            cancels = c_orders.filter(cancel_date__lt=active_period.end).values_list('cancel_date', flat=True)
                        changes = list(merge([active_period.ini], registers, cancels, [active_period.end]))
                        changes.sort()
                        u_changes = [changes[0]]
                        for ix in range(len(changes)-1): 
                            if changes[ix] != changes[ix+1]: u_changes.append(changes[ix+1])     
                        changes = u_changes                   
                        t_period = DateTime_conv(bill_period.end) - DateTime_conv(bill_period.ini)
                        for i in range(len(changes)-1):
                            #TODO: create a new manager: active_or_payed_during
                            c_ini = changes[i]
                            c_end = changes[i+1]
                            if active_or_billed: pass
                            else: active_orders = c_orders.billing_activity_during([Period(c_ini, c_end)], service)
                            metric = active_orders.count()
                            num = 1
                            while active_orders[num-1] != order: num += 1
                            #Conv to mx.DateTime, because datetime is pure crap and only have 32bit outputs
                            proportion = (DateTime_conv(c_end)-DateTime_conv(c_ini)).seconds/t_period.seconds
                            proportion = decimal.Decimal(str(proportion))
                            f_price = service.get_price(contact=order.contact, 
                                rating_metric=metric, start_metric=num, end_metric=num, start_date=c_ini, end_date=c_end)
                            final_price += f_price * proportion
                    else: raise ValueError('case not available')
            elif service.pricing_with_weight:
                if service.weight_with_is_single_order:
                    # DISK LIMIT (split into changes and price every change per metric value, recharge previously)
                   # if order.billed_until and a_ini < order.billed_until:
                   #     #FIXME: this shit sure that doesn't work
                   #     # Needs to recharge or discount       
                   #     billed_metric = order.last_bill_line.metric
                   #     d_price = service.get_price(contact=order.contact, 
                   #         rating_metric = billed_metric, start_date=a_ini, end_date=order.billed_until)
                   #     d_price *= t_period 
                   #     #TODO: only recharge, needs discount too?
                   #     if d_price < final_price: final_price -= d_price
                   # else:
                   #     for metric in order.get_metrics(ini=a_ini, end=a_end):
                   #         initial = a_ini if metric.start_date < a_ini else metric.start_date
                   #         final = metric.end_date if metric.end_date and metric.end_date < a_end else a_end
                   #         proportion = (DateTime_conv(final) - DateTime_conv(initial)).seconds/t_period.seconds
                   #         proportion = decimal.Decimal(str(proportion))
                   #         p_price = service.get_price(contact=order.contact, rating_metric=metric.value, start_date=initial, end_date=final)
                   #         final_price += p_price * proportion
                    t_period = DateTime_conv(bill_period.end) - DateTime_conv(bill_period.ini)
                    metric = order.get_metric(active_period.ini)
                    proportion = (DateTime_conv(active_period.end) - DateTime_conv(active_period.ini)).seconds/t_period.seconds
                    proportion = decimal.Decimal(str(proportion))
                    p_price = service.get_price(contact=order.contact, rating_metric=metric.value, start_date=active_period.ini, end_date=active_period.end)
                    final_price += p_price * proportion                
                else: raise ValueError('case not available')
        elif not service.has_billing_period:
            # CMS without offers (get price for their metric)
            # Maintainance without offers
            final_price = service.get_price(rating_metric=order.metric, contact=order.contact, start_date=bill_period.ini, end_date=bill_period.end)
    elif service.has_pricing_period:
        if service.pricing_effect_is_every:
            periods = service.split_pricing_period(active_period.ini, active_period.end) 
        else: 
            #periods = service.split_pricing_period(b_ini, b_end)
            periods = [Period(order.get_prev_pricing_point(bill_period.ini, lt=True), bill_period.ini)]
        t_period = DateTime_conv(bill_period.end) - DateTime_conv(bill_period.ini)
        if service.has_billing_period:
            final_price = 0
            # effect: current/every
            if service.pricing_with_orders:
                #DNS 
                for period in periods:
                    if service.pricing_effect_is_every: 
                        initial = max(bill_period.ini, period.ini)
                        final = min(bill_period.end, period.end)
                        initial = DateTime_conv(initial)
                        final = DateTime_conv(final)
                    else: 
                        initial = DateTime_conv(active_period.ini)
                        final = DateTime_conv(active_period.end)
                    proportion = decimal.Decimal(str((final - initial).seconds / t_period.seconds))
                    if service.orders_with_is_active:
                        r_orders = orders.billing_activity_during([period], service)
                    elif service.orders_with_is_registred_or_renewed:
                        r_orders = orders.registred_or_renewed_during([period], service)                        
                    elif service.orders_with_is_registred:
                        r_orders = orders.registred_during([period], service)
                    elif service.orders_with_is_renewed:
                        r_orders = orders.renewed_during([period], service)
                    num = 1
                    while r_orders[num-1] != order: num += 1
                    #NOTE: ratings per pricing period. if bp=Year and pp=monthly, rating per month.
                    #TODO: if cancelable discount non used period.  
                    partial_price = service.get_price(rating_metric=r_orders.count(), 
                        contact=order.contact, start_metric=num, end_metric=num, start_date=period.ini, end_date=period.end)
                    final_price += partial_price * proportion
                    
            elif service.pricing_with_weight:
                if service.weight_with_is_single_order:
                    # Traffic per contact
                    #FIXME: traffic doesn't be proportional
                    for period in periods:
                        initial = period.ini
                        final = period.end
                        metric = order.get_metric(initial, final)
                        #TODO: if PPP != BPP: discount time beyond BP limits
                        proportion = decimal.Decimal(str((DateTime_conv(final) - DateTime_conv(initial)).seconds / t_period.seconds))
                        partial_price = service.get_price(contact=order.contact, 
                            rating_metric=metric,start_date=initial, end_date=final) 
                        final_price += partial_price * proportion
                else: 
                    # Traffic per service with discount amount per contact
                    for period in periods:
                        initial = period.ini
                        final = period.end
                        metric = 0
                        for order in orders:
                            metric += order.get_metric(initial, final)
                            if order == order: order_metric = order.get_metric(initial, final)  
                        #TODO: if PPP != BPP: discount time beyond BP limits
                        proportion = decimal.Decimal(str((DateTime_conv(final) - DateTime_conv(initial)).seconds / t_period.seconds))
                        partial_price = service.get_price(contact=order.contact, rating_metric=metric, 
                            start_metric=(metric-order_metric), end_metric=metric, start_date=initial, end_date=final)
                        final_price += partial_price * proportion
        elif not service.has_billing_period:
            # Effect only Current (always one period)
            period = service.split_pricing_period(bill_period.ini, bill_period.end)[0]
            initial = perido.ini
            final = period.end
            if service.pricing_with_orders:
                if service.orders_with_is_registred:
                    # CMS (with offers)
                    r_orders = orders.registred_during(initial, final)
                    num = 1
                    while r_orders[num-1] != order: num += 1
                    final_price = service.get_price(rating_metric=r_orders.count(), 
                        contact=order.contact, start_metric=num, end_metric=num, start_date=initial, end_date=final)
                else: raise ValueError('case not posible')                                                
            else:
                if service.weight_with_is_single_order:
                    raise ValueError('case not posible')                                                
                else: 
                    # Maintainance (offer depends on other orders)                    
                    r_orders = orders.registred_during(initial, final)
                    metric = 0
                    for r_order in r_orders: metric += r_order.metric
                    #TODO: check if start -1 or +1 or its ok.
                    start = metric - order.metric
                    final_price = service.get_price(rating_metric=metric, contact=order.contact, 
                        start_metric=start, end_metric=metric, start_date=initial, end_date=final)   
    return final_price


def _get_pending_billing_periods(order, point, fixed_point, force_next):
    """ 
        Return entair pending billing periods and active periods per billing period like:
            {b_period: [a_periods], b_period2: [a_periods2]}
        Ignore refound and recharge periods
        
    """ 
    service = order.service
         
    if not service.has_billing_period: 
        if order.last_bill_date: return {}
        date = order.billed_until if order.billed_until else order.register_date
        b_periods = [Period(date, date)]
        a_periods = [[Period(None, None)]]
    else:   
        if order.billed_until:
            if order.get_next_billing_point(point) <= order.billed_until: return {}
            b_ini = order.get_prev_billing_point(order.billed_until)
            if order.cancel_date and order.cancel_date <= order.billed_until: return {}
            #a_ini = order.billed_until if service.discount_on_register else b_ini
            a_ini = order.billed_until
        else:
            b_ini = order.get_prev_billing_point(order.register_date)
            a_ini = order.register_date if service.discount_on_register else b_ini
       
        b_end = order.get_next_billing_point(point)
        if order.cancel_date and order.cancel_date < b_end:
            c_end = order.get_next_billing_point(order.cancel_date)
            if b_end == c_end and service.is_postpay:
                b_end = order.get_prev_billing_point(point)
                a_end = b_end
            #elif b_end == c_end and fixed_point: 
            #    a_end = order.cancel_date if point > order.cancel_date else point 
            else:
                b_end = c_end
                a_end = order.cancel_date if service.discount_on_cancel else c_end         
        else:
            if service.is_postpay: b_end = order.get_prev_billing_point(point)
            elif service.is_prepay: b_end = order.get_next_billing_point(point)
            if force_next: 
                next_fixed = order.get_next_billing_point(point, fixed=True)
                if b_end < next_fixed: b_end = order.get_next_billing_point(next_fixed)
            a_end = b_end if not fixed_point else point 

        if fixed_point and point < a_end: a_end = point 
        
        
        b_periods = service.split_billing_period(b_ini, b_end, point=order.register_date)
        a_periods = []
        for a_period in service.split_billing_period(a_ini, a_end, point=order.register_date): 
            if service.discount_on_disable:
                _a_periods = order.active_periods_during(a_period)
            else: _a_periods = [a_period]
            if service.pricing_with_weight and service.metric_with_changes:
                # bill line per change
                new_a_periods = []
                for period in _a_periods:
                    for c_period in order.get_metric(period.ini, period.end, gt_ini=False):
                        end = min(c_period.end, metric.end_date)
                        new_a_periods.append(Period(c_period.ini, end))        
                _a_periods = new_a_periods
            a_periods.append(_a_periods)

        return dict(iter(list(zip(b_periods, a_periods)))) 


def get_recharge_and_refound_periods(order):

    if not order.billed_until: return {}, {}
    #TODO: if not prepay return {} {}
    
    #TODO: get only cancels and disables created > last_bill_moment
    
    service = order.service
    ini = order.last_bill_date
    end = order.billed_until
    
    b_periods = service.split_billing_period(order.get_prev_billing_point(ini), order.get_next_billing_point(end))
    a_periods = service.split_billing_period(ini, end)
   
    refound_periods = {}
    recharge_periods = {}
    
    if service.refound_on_disable and not order.disabled_on(ini):
        for ix in range(len(a_periods)):
            r_periods = []
            a_ini = a_periods[ix].ini
            a_end = a_periods[ix].end
            # Lookup for desactivations create after bill_date and active during a_periods.
            for d_period in order.contract.deactivationperiod_set.filter(Q(register_date__gt=ini, 
                            start_date__lt=a_end) & 
                            Q(Q(end_date__isnull=True) | Q(end_date__gt=a_ini)) & 
                            Q(Q(annulation_date__isnull=True) | Q(annulation_date__gt=F('start_date')))):
                            
                p_end = min(a_end, d_period.end_date) if d_period.end_date else a_end
                if d_period.cancel_date:
                    p_end = min(p_end, d_period.cancel_date)
                p_ini = max(d_period.start_date, a_.ini)
                r_periods.append(Period(p_ini, p_end))
            if r_periods:
                refound_periods[b_periods[ix]] = r_periods           
        
    if service.recharge_on_disable and order.disabled_on(ini):
        for ix in range(len(a_periods)):
            a_ini = a_periods[ix].ini
            a_end = a_periods[ix].end
            #Lookup active deactivationperiods when ini that have cancels between a_period. 
            for d_period in order.contract.deactivationperiod_set.filter(Q(register_date__lt=ini, 
                                 annulation_date__gt=ini, annulation_date__lt=min(F('end_date'), a_end), 
                                 start_date__lt=a_end) & Q(Q(end_date__isnull=True)|Q(end_date__gt=a_ini))):
                                
                
                p_ini = max(d_period.cancel_date, d_period.start_date, a_ini)
                p_end = d_period.end_date if d_period.end_date else a_end
                period = Period(p_ini, p_end)
                if recharge_periods.has_key(b_periods[ix]): 
                    recharge_periods[b_periods[ix]].append(period)
                else: recharge_periods[b_periods[ix]] = [period]
            
            
    if service.refound_on_cancel and order.cancel_date and order.cancel_date < end:
        for ix in range(len(a_periods)):
            if a_periods[ix].end > order.cancel_date:
                period = Period(order.cancel_date, end)
                if refound_periods.has_key(b_periods[ix]):
                    refound_periods[b_periods[ix]].append(period)
                else: refound_periods[b_periods[ix]] = [period]            
            
            
            
    if service.refound_on_cancel and order.cancel_date and order.cancel_date < end:
        for ix in range(len(a_periods)):
            if a_periods[ix].end > order.cancel_date:
                period = Period(order.cancel_date, end)
                if refound_periods.has_key(b_periods[ix]):
                    refound_periods[b_periods[ix]].append(period)
                else: refound_periods[b_periods[ix]] = [period]
    
    if service.refound_on_weight:
        billed_metric = order.get_metric(ini)
        for ix in range(len(a_periods)):
            for metric in order.get_metrics(period.ini, period.end, gt_ini=True):
                end = min(a_periods[ix].end, metric.end_date)
                if metric < billed_metric: 
                    period = Period(metric.start_date, end)
                    if refound_periods.has_key(b_periods[ix]):
                        refound_periods[b_periods[ix]].append(period)
                    else: refound_periods[b_periods[ix]] = [period]     
                      
    if service.recharge_on_weight:
        billed_metric = order.get_metric(ini)
        for ix in range(len(a_periods)):
            for metric in order.get_metrics(a_periods[ix].ini, a_periods[ix].end, gt_ini=True):
                end = min(a_periods[ix].end, metric.end_date)
                if metric > billed_metric: 
                    r_periods.append(Period(metric.start_date, end))
                    period = Period(metric.start_date, end)
                    if recharge_periods[b_periods[ix]]: 
                        recharge_periods[b_periods[ix]].append(period)
                    else: recharge_periods[b_periods[ix]] = [period]
                        
    return recharge_periods, refound_periods
    

def _create_bills(Order, contact, billing_orders, pricing_orders, point, fixed_point, force_next, create_new_open, commit):
    #from models import Invoice, AmendmentInvoice, Fee, AmendmentFee
    s_billing_orders = group_by(Order, 'service', billing_orders, dictionary=True)
    s_pricing_orders = group_by(Order, 'service', pricing_orders, dictionary=True)
    
    #bill_lines = BillLinesBundle()
    bill_lines = []
    for service in s_billing_orders:
        bill_lines.extend(_create_bill_lines(service, s_billing_orders[service], 
                         s_pricing_orders[service], contact, point=point, 
                         fixed_point=fixed_point, force_next=force_next, commit=commit))
    
    return create_bills(bill_lines, contact)


def _create_bill_lines(service, billing_orders, pricing_orders, contact, point, fixed_point, force_next, commit):
    #from models import BillLine, AmendedBillLine
    now = datetime.now()
    bill_lines = []
    for order in billing_orders:
        periods = order.get_pending_billing_periods(point=point, fixed_point=fixed_point, force_next=force_next)

        #TODO: DRY it
        for b_period in periods:
            for a_period in periods[b_period]:
                price = order.get_price(pricing_orders, b_period, a_period)
                bill_lines.append(create_bill_line(order, price, a_period.ini, a_period.end))
        
        recharge_periods, refound_periods = get_recharge_and_refound_periods(order)
        for b_period in refound_periods:
            for a_period in refound_periods[b_period]:
                price = 0
                for line in get_invoice_lines(order.pk, a_period.ini, a_period.end):
                    ini = line.initial_date if line.initial_date > a_period.ini else a_period.ini
                    end = line.final_date if line.final_date < a_period.end else a_period.end
                    price += ((end-ini).days / (line.final_date-line.initial_date).days) * line.price
#                price = order.get_price(pricing_orders, b_period, a_period)
                bill_lines.append(create_bill_line(order, -price, a_period.ini, a_period.end ))
                
        for b_period in recharge_periods:
            for a_period in recharge_periods[b_period]:
                price = order.get_price(pricing_orders, b_period, a_period)
                bill_lines.append(create_bill_line(order, price, b_period, a_period))

#        # Update Order
        if commit:
            a_periods = []
            for _periods in list(merge(merge(periods.values(), refound_periods.values()),recharge_periods.values())):
                for _period in _periods: a_periods.append(_period)
            if a_periods:
                billed_until = sorted(a_periods, key=lambda a_periods: a_periods.end)[-1].end
                order.billed_until = billed_until
                order.last_bill_date = now
                order.save()
            
    return bill_lines

