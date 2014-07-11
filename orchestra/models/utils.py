from django.conf import settings
from django.db.models import loading, Manager
from django.utils import importlib


def get_model(label, import_module=True):
    app_label, model_name = label.split('.')
    model = loading.get_model(app_label, model_name)
    if model is None:
        # Sometimes the models module is not yet imported
        for app in settings.INSTALLED_APPS:
            if app.endswith(app_label):
                app_label = app
        importlib.import_module('%s.%s' % (app_label, 'admin'))
        return loading.get_model(*label.split('.'))
    return model


def queryset_as_manager(qs_class):
    # Allow chained managers
    # Based on http://djangosnippets.org/snippets/562/#c2486
    class ChainerManager(Manager):
        def __init__(self):
            super(ChainerManager,self).__init__()
            self.queryset_class = qs_class
        
        def get_query_set(self):
            return self.queryset_class(self.model)
        
        def __getattr__(self, attr, *args):
            try:
                return getattr(type(self), attr, *args)
            except AttributeError:
                return getattr(self.get_query_set(), attr, *args)
    return ChainerManager()


def get_field_value(obj, field_name):
    names = field_name.split('__')
    rel = getattr(obj, names.pop(0))
    for name in names:
        try:
            rel = getattr(rel, name)
        except AttributeError:
            # maybe is a query manager
            rel = getattr(rel.get(), name)
    return rel


def get_model_field_path(origin, target):
    """ BFS search on model relaion fields """
    queue = []
    queue.append(([origin], []))
    while queue:
        model, path = queue.pop(0)
        if len(model) > 4:
            msg = "maximum recursion depth exceeded while looking for %s"
            raise RuntimeError(msg % target)
        node = model[-1]
        if node == target:
            return path
        for field in node._meta.fields:
            if field.rel:
                new_model = list(model)
                new_model.append(field.rel.to)
                new_path = list(path)
                new_path.append(field.name)
                queue.append((new_model, new_path))
