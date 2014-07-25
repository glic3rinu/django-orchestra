def group_by(qset, *fields):
    """ group_by iterator with support for multiple nested fields """
    def nest(objects, ix):
        objs = []
        result = []
        first = True
        for obj in objects:
            current = getattr(obj, fields[ix])
            if first or current == previous:
                objs.append(obj)
            else:
                if ix < len(fields)-1:
                    objs = nest(list(objs), ix+1)
                result.append((previous, objs))
                objs = [obj]
            previous = current
            first = False
        if ix < len(fields)-1:
            objs = nest(list(objs), ix+1)
        result.append((current, objs))
        return result
    
    objs = []
    first = True
    for obj in qset.order_by(*fields):
        current = getattr(obj, fields[0])
        if first or current == previous:
            objs.append(obj)
        else:
            if len(fields) > 1:
                objs = nest(objs, 1)
            yield previous, objs
            objs = [obj]
        previous = current
        first = False
    if len(fields) > 1:
        objs = nest(objs, 1)
    yield current, objs
