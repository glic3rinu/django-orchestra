from django.db import models

from ..models import User


class Register(object):
    def __init__(self):
        self._registry = {}
    
    def __contains__(self, key):
        return key in self._registry
    
    def register(self, name, model):
        if name in self._registry:
            raise KeyError("%s already registered" % name)
        def has_role(user):
            try:
                getattr(user, name)
            except models.DoesNotExist:
                return False
            return True
        setattr(User, 'has_%s' % name, has_role)
        self._registry[name] = model
    
    def get(self):
        return self._registry


roles = Register()
