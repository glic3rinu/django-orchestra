import sys

from django.utils.translation import ugettext_lazy as _

from orchestra.utils.python import AttrDict


def _compute_steps(rates, metric):
    value = 0
    num = len(rates)
    accumulated = 0
    barrier = 1
    next_barrier = None
    end = False
    ix = 0
    steps = []
    while ix < num and not end:
        fold = 1
        # Multiple contractions
        while ix < num-1 and rates[ix] == rates[ix+1]:
            ix += 1
            fold += 1
        if ix+1 == num:
            quantity = metric - accumulated
            next_barrier = quantity
        else:
            quantity = rates[ix+1].quantity - max(rates[ix].quantity, 1)
            next_barrier = quantity
            if rates[ix+1].price > rates[ix].price:
                quantity *= fold
            if accumulated+quantity > metric:
                quantity = metric - accumulated
                end = True
        price = rates[ix].price
        steps.append(AttrDict(**{
            'quantity': quantity,
            'price': price,
            'barrier': barrier,
        }))
        accumulated += quantity
        barrier += next_barrier
        value += quantity*price
        ix += 1
    return value, steps


def _standardize(rates):
    """
    Support for incomplete rates
    When first rate (quantity=5, price=10) defaults to nominal_price
    """
    std_rates = []
    minimal = rates[0].quantity
    for rate in rates:
        #if rate.quantity == 0:
        #    rate.quantity = 1
        if rate.quantity == minimal and rate.quantity > 0:
            service = rate.service
            rate_class = type(rate)
            std_rates.append(
                rate_class(service=service, plan=rate.plan, quantity=0, price=service.nominal_price)
            )
        std_rates.append(rate)
    return std_rates


def step_price(rates, metric):
    if rates.query.order_by != ['plan', 'quantity']:
        raise ValueError("rates queryset should be ordered by 'plan' and 'quantity'")
    # Step price
    group = []
    minimal = (sys.maxsize, [])
    for plan, rates in rates.group_by('plan').items():
        rates = _standardize(rates)
        value, steps = _compute_steps(rates, metric)
        if plan.is_combinable:
            group.append(steps)
        else:
            minimal = min(minimal, (value, steps), key=lambda v: v[0])
    if len(group) == 1:
        value, steps = _compute_steps(rates, metric)
        minimal = min(minimal, (value, steps), key=lambda v: v[0])
    elif len(group) > 1:
        # Merge
        steps = []
        for rates in group:
            steps += rates
        steps.sort(key=lambda s: s.price)
        result = []
        counter = 0
        value = 0
        ix = 0
        targets = []
        while counter < metric:
            barrier = steps[ix].barrier
            if barrier <= counter+1:
                price = steps[ix].price
                quantity = steps[ix].quantity
                if quantity + counter > metric:
                    quantity = metric - counter
                else:
                    for target in targets:
                        if counter + quantity >= target:
                            quantity = (counter+quantity+1) - target
                            steps[ix].quantity -= quantity
                            if not steps[ix].quantity:
                                steps.pop(ix)
                            break
                    else:
                        steps.pop(ix)
                counter += quantity
                value += quantity*price
                if result and result[-1].price == price:
                    result[-1].quantity += quantity
                else:
                    result.append(AttrDict(quantity=quantity, price=price))
                ix = 0
                targets = []
            else:
                targets.append(barrier)
                ix += 1
        minimal = min(minimal, (value, result), key=lambda v: v[0])
    return minimal[1]
step_price.verbose_name = _("Step price")
step_price.help_text = _("All rates with a quantity lower or equal than the metric are applied. "
                         "Nominal price will be used when initial block is missing.")


def match_price(rates, metric):
    if rates.query.order_by != ['plan', 'quantity']:
        raise ValueError("rates queryset should be ordered by 'plan' and 'quantity'")
    candidates = []
    selected = False
    prev = None
    rates = _standardize(rates.distinct())
    for rate in rates:
        if prev:
            if prev.plan != rate.plan:
                if not selected and prev.quantity <= metric:
                    candidates.append(prev)
                selected = False
            if not selected and rate.quantity > metric:
                if prev.quantity <= metric:
                    candidates.append(prev)
                    selected = True
        prev = rate
    if not selected and prev.quantity <= metric:
        candidates.append(prev)
    candidates.sort(key=lambda r: r.price)
    if candidates:
        return [AttrDict(**{
            'quantity': metric,
            'price': candidates[0].price,
        })]
    return None
match_price.verbose_name = _("Match price")
match_price.help_text = _("Only <b>the rate</b> with a) inmediate inferior metric and b) lower price is applied. "
                          "Nominal price will be used when initial block is missing.")


def best_price(rates, metric):
    if rates.query.order_by != ['plan', 'quantity']:
        raise ValueError("rates queryset should be ordered by 'plan' and 'quantity'")
    candidates = []
    for plan, rates in rates.group_by('plan').items():
        rates = _standardize(rates)
        plan_candidates = []
        for rate in rates:
            if rate.quantity > metric:
                break
            if plan_candidates:
                ant = plan_candidates[-1]
                if ant.price == rate.price:
                    # Multiple plans support
                    ant.fold += 1
                else:
                    ant.quantity = rate.quantity-1
                    plan_candidates.append(AttrDict(
                        price=rate.price,
                        quantity=metric,
                        fold=1,
                    ))
            else:
                plan_candidates.append(AttrDict(
                    price=rate.price,
                    quantity=metric,
                    fold=1,
                ))
        candidates.extend(plan_candidates)
    results = []
    accumulated = 0
    for candidate in sorted(candidates, key=lambda c: c.price):
        if candidate.quantity < accumulated:
            # Out of barrier
            continue
        candidate.quantity *= candidate.fold
        if accumulated+candidate.quantity > metric:
            quantity = metric - accumulated
        else:
            quantity = candidate.quantity
        accumulated += quantity
        if quantity:
            if results and results[-1].price == candidate.price:
                results[-1].quantity += quantity
            else:
                results.append(AttrDict(**{
                    'quantity': quantity,
                    'price': candidate.price
                }))
    return results
best_price.verbose_name = _("Best price")
best_price.help_text = _("Produces the best possible price given all active rating lines (those with quantity lower or equal to the metric).")
