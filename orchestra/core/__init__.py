class Service(object):
    _registry = {}
    
    def register(self, model, **kwargs):
        if model in self._registry:
            raise KeyError("%s already registered" % str(model))
        plural = kwargs.get('verbose_name_plural', model._meta.verbose_name_plural)
        self._registry[model] = {
            'verbose_name': kwargs.get('verbose_name', model._meta.verbose_name),
            'verbose_name_plural': plural,
            'menu': kwargs.get('menu', True)
        }
    
    def get(self):
        return self._registry


services = Service()
