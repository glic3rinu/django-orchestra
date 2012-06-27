class Period(object):
    def __init__(self, start, end):
        super(Period, self).__init__()
        self.start = start
        self.end = end
        
    def __unicode__(self):
        return "%s - %s" % (self.start, self.end)    

    @property
    def start_date(self):
        return self.start
    
    @property
    def end_date(self):
        return self.end


def union(self, other):
    """ self and other are objects with start_date and end_date methods implemented """
    if other.start_date < self.start_date:
        if not other.end_date or other.end_date > self.start_date:
            return [Period(other.start_date, self.end_date)]
        else:
            return [Period(other.start_date, other.end_date), Period(self.start_date, self.end_date)]
    else:
        if not self.end_date or other.start_date < self.end_date:
            return [Period(self.start_date, other.end_date)]
        else:
            return [Period(self.start_date, self.end_date), Period(other.start_date, other.end_date)]


def intersection(self, other):
    """ self and other are objects with start_date and end_date methods implemented """
    if not self.end_date or other.start_date < self.end_date:
        ini = other.start_date if other.start_date > self.start_date else self.start_date
    else: return None
    if not other.end_date or other.end_date > self.start_date:
        if other.end_date and self.end_date:
            end = other.end_date if other.end_date < self.end_date else self.end_date
        # return None before datetime.max
        elif not other.end_date: end = other.end_date
        else: end = self.end_date
    else: return None
    return Period(ini, end)   


def periods_intersection(selfs, others):
    if not selfs: return []
    if not others: return []
    intersection_periods = []
    for self in selfs:
        for other in others:
            current_intersection = intersection(self, other)
            if not current_intersection:
                break
            intersection_periods.append(current_intersection)
    return intersection_periods


def periods_union(selfs, others):
    """ selfs and others are lists of periods """ 
    if not selfs: return others
    if not others: return selfs
    union_periods = []
    for current in list(selfs)+list(others):
        if not union_periods:
            union_periods = [current]
        else:
            _periods = []
            for period in union_periods:
                _periods += union(period, current)
            union_periods = _periods
    return union_periods    

