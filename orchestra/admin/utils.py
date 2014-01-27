from django.contrib import admin
from django.db import models


def get_modeladmin(model, import_module=True):
    """ returns the modeladmin registred for model """
    for k,v in admin.site._registry.iteritems():
        if k is model:
            if v is None and import_module:
                # Sometimes the admin module is not yet imported
                import_module('%s.%s' % (model._meta.app_label, 'admin'))
                get_modeladmin(model, import_module=False)
            return v


def insertattr(model, name, value, weight=0):
    """ Inserts attribute to a modeladmin """
    is_model = models.Model in model.__mro__
    modeladmin = get_modeladmin(model) if is_model else model
    # Avoid inlines defined on parent class be shared between subclasses
    # Seems that if we use tuples they are lost in some conditions like changing
    # the tuple in modeladmin.__init__
    if not getattr(modeladmin, name):
        setattr(type(modeladmin), name, [])
    
    inserted_attrs = getattr(modeladmin, '__inserted_attrs__', {})
    if not name in inserted_attrs:
        weights = {}
        if hasattr(modeladmin, 'weights') and name in modeladmin.weights:
            weights = modeladmin.weights.get(name)
        inserted_attrs[name] = [ (attr, weights.get(attr, 0)) for attr in getattr(modeladmin, name) ]
    
    inserted_attrs[name].append((value, weight))
    inserted_attrs[name].sort(key=lambda a: a[1])
    setattr(modeladmin, name, [ attr[0] for attr in inserted_attrs[name] ])
    setattr(modeladmin, '__inserted_attrs__', inserted_attrs)

