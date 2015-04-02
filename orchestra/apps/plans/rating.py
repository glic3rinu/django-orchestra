import sys

from django.utils.translation import string_concat, ugettext_lazy as _

from orchestra.utils.python import AttrDict


def _compute(rates, metric):
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
            quantity = rates[ix+1].quantity - rates[ix].quantity
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


def _prepend_missing(rates):
    """
    Support for incomplete rates
    When first rate (quantity=5, price=10) defaults to nominal_price
    """
    if rates:
        first = rates[0]
        if first.quantity == 0:
            first.quantity = 1
        elif first.quantity > 1:
            if not isinstance(rates, list):
                rates = list(rates)
            service = first.service
            rate_class = type(first)
            rates.insert(0,
                rate_class(service=service, plan=first.plan, quantity=1, price=service.nominal_price)
            )
    return rates


def step_price(rates, metric):
    # Step price
    group = []
    minimal = (sys.maxsize, [])
    for plan, rates in rates.group_by('plan').items():
        rates = _prepend_missing(rates)
        value, steps = _compute(rates, metric)
        if plan.is_combinable:
            group.append(steps)
        else:
            minimal = min(minimal, (value, steps), key=lambda v: v[0])
    if len(group) == 1:
        value, steps = _compute(rates, metric)
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
step_price.help_text = _("All price rates with a lower metric are applied.")


def match_price(rates, metric):
    candidates = []
    selected = False
    prev = None
    rates = _prepend_missing(rates.distinct())
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
match_price.help_text = _("Only the rate with inmediate inferior metric is applied.")
