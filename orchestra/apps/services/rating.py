import sys

from orchestra.utils.python import AttributeDict


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
        steps.append(AttributeDict(**{
            'quantity': quantity,
            'price': price,
            'barrier': barrier,
        }))
        accumulated += quantity
        barrier += next_barrier
        value += quantity*price
        ix += 1
    return value, steps


def step_price(rates, metric):
    # Step price
    group = []
    minimal = (sys.maxint, [])
    for plan, rates in rates.group_by('plan').iteritems():
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
                    result.append(AttributeDict(quantity=quantity, price=price))
                ix = 0
                targets = []
            else:
                targets.append(barrier)
                ix += 1
        minimal = min(minimal, (value, result), key=lambda v: v[0])
    return minimal[1]


def match_price(rates, metric):
    candidates = []
    selected = False
    prev = None
    for rate in rates.distinct():
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
        return [AttributeDict(**{
            'quantity': metric,
            'price': candidates[0].price,
        })]
    return None
