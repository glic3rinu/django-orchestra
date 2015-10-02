def cached(func):
    """ 
    DEPRECATED in favour of lru_cahce
    caches func return value
    """
    def cached_func(self, *args, **kwargs):
        # id(self) prevents sharing within subclasses
        attr = '_cached_%s_%i' % (func.__name__, id(self))
        key = (args, tuple(kwargs.items()))
        try:
            return getattr(self, attr)[key]
        except KeyError:
            value = func(self, *args, **kwargs)
            getattr(self, attr)[key] = value
        except AttributeError:
            value = func(self, *args, **kwargs)
            setattr(self, attr, {key: value})
        return value
    return cached_func
