import sys


def best_price(rates, metric):
    rates = rates.order_by('metric').order_by('plan')
    ix = 0
    steps = []
    num = rates.count()
    while ix < num:
        if ix+1 == num or rates[ix].plan != rates[ix+1].plan:
            number = metric
        else:
            number = rates[ix+1].metric - rates[ix].metric
        steps.append({
            'number': sys.maxint,
            'price': rates[ix].price
        })
        ix += 1
    
    steps.sort(key=lambda s: s['price'])
    acumulated = 0
    for step in steps:
        previous = acumulated
        acumulated += step['number']
        if acumulated >= metric:
            step['number'] = metric - previous
            yield step
            raise StopIteration
        yield step


def match_price(rates, metric):
    minimal = None
    for plan, rates in rates.order_by('-metric').group_by('plan'):
        if minimal is None:
            minimal = rates[0].price
        else:
            minimal = min(minimal, rates[0].price)
    return [{
        'number': sys.maxint,
        'price': minimal
    }]
