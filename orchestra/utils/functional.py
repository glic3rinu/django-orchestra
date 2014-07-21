def cached(func):
    """ caches func return value """
    def cached_func(self, *args, **kwargs):
        attr = '_cached_' + func.__name__
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

