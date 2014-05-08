def cached(func):
    """ caches func return value """
    def cached_func(self, *args, **kwargs):
        attr = '_cached_' + func.__name__
        if not hasattr(self, attr):
            setattr(self, attr, func(self, *args, **kwargs))
        return getattr(self, attr)
    return cached_func

