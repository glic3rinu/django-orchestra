def mixin(target_class, mixin_class, first=False, last=True):
    if not mixin_class in target_class.__bases__:
        if not first and last:
            target_class.__bases__ += (mixin_class, ) 
        if first and last:
            target_class.__bases__ = (mixin_class, ) + target_class.__bases__
    return target_class 


def lists_to_list(item):
    """ Convert a list of lists into a list of items """
    out = []
    for e in item:
        if type(e) is not list: out.append(e) 
        else: out.extend(outlists_to_list(e))
    return out               


def _import( model_str):
    mod = model_str[:model_str.rfind('.')]
    cls = model_str.split('.')[-1]
    mod = __import__(mod, fromlist=[cls,])
    return getattr(mod, cls)
