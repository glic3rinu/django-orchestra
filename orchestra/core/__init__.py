from django.utils.translation import string_concat

from ..utils.python import AttrDict


class Register(object):
    def __init__(self, verbose_name=None):
        self._registry = {}
        self.verbose_name = verbose_name
    
    def __contains__(self, key):
        return key in self._registry
    
    def __getitem__(self, key):
        return self._registry[key]
    
    def register(self, model, **kwargs):
        if model in self._registry:
            raise KeyError("%s already registered" % model)
        if 'verbose_name' not in kwargs:
            kwargs['verbose_name'] = model._meta.verbose_name
        if 'verbose_name_plural' not in kwargs:
            kwargs['verbose_name_plural'] = model._meta.verbose_name_plural
        self._registry[model] = AttrDict(**kwargs)
    
    def register_view(self, view_name, **kwargs):
        if view_name in self._registry:
            raise KeyError("%s already registered" % view_name)
        if 'verbose_name' not in kwargs:
            raise KeyError("%s verbose_name is required for views" % view_name)
        if 'verbose_name_plural' not in kwargs:
            kwargs['verbose_name_plural'] = string_concat(kwargs['verbose_name'], 's')
        self._registry[view_name] = AttrDict(**kwargs)
    
    def get(self, *args):
        if args:
            return self._registry[args[0]]
        return self._registry


services = Register(verbose_name='Services')
# TODO rename to something else
accounts = Register(verbose_name='Accounts')
administration = Register(verbose_name='Administration')
