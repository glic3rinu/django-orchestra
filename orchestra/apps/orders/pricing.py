import sys


def best_price(rates, metric, cache={}):
    steps = cache.get('steps')
    if not steps:
        rates = rates.order_by('quantity').order_by('plan')
        ix = 0
        steps = []
        num = rates.count()
        while ix < num:
            if ix+1 == num or rates[ix].plan != rates[ix+1].plan:
                quantity = sys.maxint
            else:
                quantity = rates[ix+1].quantity - rates[ix].quantity
            steps.append({
                'quantity': quantity,
                'price': rates[ix].price
            })
            ix += 1
        steps.sort(key=lambda s: s['price'])
        cache['steps'] = steps
    return steps


def match_price(rates, metric, cache={}):
    minimal = None
    for plan, rates in rates.order_by('-metric').group_by('plan'):
        if minimal is None:
            minimal = rates[0].price
        else:
            minimal = min(minimal, rates[0].price)
    return [{
        'quantity': sys.maxint,
        'price': minimal
    }]
