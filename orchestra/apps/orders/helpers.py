import inspect

from orchestra.apps.accounts.models import Account


def get_related_objects(origin, max_depth=2):
    """
    Introspects origin object and return the first related service object
    
    WARNING this is NOT an exhaustive search but a compromise between cost and
            flexibility. A more comprehensive approach may be considered if
            a use-case calls for it.
    """
    
    def related_iterator(node):
        for field in node._meta.virtual_fields:
            if hasattr(field, 'ct_field'):
                yield getattr(node, field.name)
        for field in node._meta.fields:
            if field.rel:
                yield getattr(node, field.name)
    
    # BFS model relation transversal
    queue = [[origin]]
    while queue:
        models = queue.pop(0)
        if len(models) > max_depth:
            return None
        node = models[-1]
        if len(models) > 1:
            if hasattr(node, 'account') or isinstance(node, Account):
                return node
        for related in related_iterator(node):
            if related and related not in models:
                new_models = list(models)
                new_models.append(related)
                queue.append(new_models)

def get_register_or_cancel_events(porders, ini, end):
    assert ini > end, "ini > end"
    CANCEL = 'cancel'
    REGISTER = 'register'
    changes = {}
    counter = 0
    for order in porders:
        if order.cancelled_on:
            cancel = order.cancelled_on
            if order.billed_until and order.cancelled_on < order.billed_until:
                cancel = order.billed_until
            if cancel > ini and cancel < end:
                changes.setdefault(cancel, [])
                changes[cancel].append(CANCEL)
        if order.registered_on < ini:
            counter += 1
        elif order.registered_on < end:
            changes.setdefault(order.registered_on, [])
            changes[order.registered_on].append(REGISTER)
    pointer = ini
    total = float((end-ini).days)
    for date in changes.keys().sort():
        for change in changes[date]:
            if change is CANCEL:
                counter -= 1
            else:
                counter += 1
        yield counter, (date-pointer).days/total
        pointer = date


def get_register_or_renew_events(handler, porders, ini, end):
    total = float((end-ini).days)
    for sini, send in handler.get_pricing_slots(ini, end):
        counter = 0
        for order in porders:
            if order.registered_on > sini and order.registered_on < send:
                counter += 1
            elif order.billed_until > send or order.cancelled_on > send:
                counter += 1
        yield counter, (send-sini)/total
