from ..utils.python import AttrDict


class Register(object):
    def __init__(self):
        self._registry = {}
    
    def __contains__(self, key):
        return key in self._registry
    
    def __getitem__(self, key):
        return self._registry[key]
    
    def register(self, model, **kwargs):
        if model in self._registry:
            raise KeyError("%s already registered" % str(model))
        plural = kwargs.get('verbose_name_plural', model._meta.verbose_name_plural)
        self._registry[model] = AttrDict(**{
            'verbose_name': kwargs.get('verbose_name', model._meta.verbose_name),
            'verbose_name_plural': plural,
            'menu': kwargs.get('menu', True),
        })
    
    def get(self, *args):
        if args:
            return self._registry[arg[0]]
        return self._registry


services = Register()
# TODO rename to something else
accounts = Register()
