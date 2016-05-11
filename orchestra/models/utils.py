from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.apps import apps
import importlib


def get_model(label, import_module=True):
    app_label, model_name = label.split('.')
    model = apps.get_model(app_label, model_name)
    if model is None:
        # Sometimes the models module is not yet imported
        for app in settings.INSTALLED_APPS:
            if app.endswith(app_label):
                app_label = app
        importlib.import_module('%s.%s' % (app_label, 'admin'))
        return apps.get_model(*label.split('.'))
    return model


def has_db_field(obj, field_name):
    try:
        obj._meta.get_field(field_name)
    except FieldDoesNotExist:
        return False
    return True


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
            msg = "maximum recursion depth exceeded while looking for %s from %s"
            raise RuntimeError(msg % (target, origin))
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
    raise LookupError("Path does not exists between '%s' and '%s' models" % (origin, target))
