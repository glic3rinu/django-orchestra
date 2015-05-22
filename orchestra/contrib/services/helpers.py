def get_chunks(porders, ini, end, ix=0):
    if ix >= len(porders):
        return [[ini, end, []]]
    order = porders[ix]
    ix += 1
    bu = getattr(order, 'new_billed_until', order.billed_until)
    if not bu or bu <= ini or order.registered_on >= end:
        return get_chunks(porders, ini, end, ix=ix)
    result = []
    if order.registered_on < end and order.registered_on > ini:
        ro = order.registered_on
        result = get_chunks(porders, ini, ro, ix=ix)
        ini = ro
    if bu < end:
        result += get_chunks(porders, bu, end, ix=ix)
        end = bu
    chunks = get_chunks(porders, ini, end, ix=ix)
    for chunk in chunks:
        chunk[2].insert(0, order)
        result.append(chunk)
    return result


def cmp_billed_until_or_registered_on(a, b):
    """
    1) billed_until greater first
    2) registered_on smaller first
    """
    if a.billed_until == b.billed_until:
        # Use pk which is more reliable than registered_on date
        return a.id-b.id
    elif a.billed_until and b.billed_until:
        return (b.billed_until-a.billed_until).days
    elif a.billed_until:
        return (b.registered_on-a.billed_until).days
    return (b.billed_until-a.registered_on).days


class Interval(object):
    def __init__(self, ini, end, order=None):
        self.ini = ini
        self.end = end
        self.order = order
    
    def __len__(self):
        return max((self.end-self.ini).days, 0)
    
    def __sub__(self, other):
        remaining = []
        if self.ini < other.ini:
            remaining.append(Interval(self.ini, min(self.end, other.ini), self.order))
        if self.end > other.end:
            remaining.append(Interval(max(self.ini,other.end), self.end, self.order))
        return remaining
    
    def __repr__(self):
        return "<ini:{ini}/end:{end}>".format(
            ini=self.ini.strftime('%Y-%-m-%-d'),
            end=self.end.strftime('%Y-%-m-%-d')
        )
    
    def intersect(self, other, remaining_self=None, remaining_other=None):
        if remaining_self is not None:
            remaining_self += (self - other)
        if remaining_other is not None:
            remaining_other += (other - self)
        result = Interval(max(self.ini, other.ini), min(self.end, other.end), self.order)
        if len(result)>0:
            return result
        else:
            return None
    
    def intersect_set(self, others, remaining_self=None, remaining_other=None):
        intersections = []
        for interval in others:
            intersection = self.intersect(interval, remaining_self, remaining_other)
            if intersection:
                intersections.append(intersection)
        return intersections


def get_intersections(order_intervals, compensations):
    intersections = []
    for compensation in compensations:
        intersection = compensation.intersect_set(order_intervals)
        length = 0
        for intersection_interval in intersection:
            length += len(intersection_interval)
        intersections.append((length, compensation))
    return sorted(intersections, key=lambda i: i[0])


def intersect(compensation, order_intervals):
    # Intervals should not overlap
    compensated = []
    not_compensated = []
    unused_compensation = []
    for interval in order_intervals:
        compensated.append(compensation.intersect(interval, unused_compensation, not_compensated))
    return (compensated, not_compensated, unused_compensation)


def apply_compensation(order, compensation):
    remaining_order = []
    remaining_compensation = []
    applied_compensation = compensation.intersect_set(order, remaining_compensation, remaining_order)
    return applied_compensation, remaining_order, remaining_compensation


def update_intersections(not_compensated, compensations):
    # TODO can be optimized
    compensation_intervals = []
    for __, compensation in compensations:
        compensation_intervals.append(compensation)
    return get_intersections(not_compensated, compensation_intervals)


def compensate(order, compensations):
    remaining_interval = [order]
    ordered_intersections = get_intersections(remaining_interval, compensations)
    applied_compensations = []
    remaining_compensations = []
    while ordered_intersections and ordered_intersections[len(ordered_intersections)-1][0]>0:
        # Apply the first compensation:
        __, compensation = ordered_intersections.pop()
        (applied_compensation, remaining_interval, remaining_compensation) = apply_compensation(remaining_interval, compensation)
        remaining_compensations += remaining_compensation
        applied_compensations += applied_compensation
        ordered_intersections = update_intersections(remaining_interval, ordered_intersections)
    for __, compensation in ordered_intersections:
        remaining_compensations.append(compensation)
    return remaining_compensations, applied_compensations
