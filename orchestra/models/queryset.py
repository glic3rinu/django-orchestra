from collections import OrderedDict

from .utils import get_field_value


def group_by(qset, *fields):
    """ 100% in python in order to preserve original order_by """
    first = OrderedDict()
    num = len(fields)
    for obj in qset:
        ix = 0
        group = first
        while ix < num:
            try:
                current = get_field_value(obj, fields[ix])
            except AttributeError:
                # Intermediary relation does not exists
                current = None
            if ix < num-1:
                try:
                    group = group[current]
                except KeyError:
                    group[current] = OrderedDict()
                    group = group[current]
            else:
                try:
                    group[current].append(obj)
                except KeyError:
                    group[current] = [obj]
            ix += 1
    return first
