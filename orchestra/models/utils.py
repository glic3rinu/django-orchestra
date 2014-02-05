from django.conf import settings
from django.db.models import loading
from django.utils import importlib


def get_model(label, import_module=True):
    """ returns the modeladmin registred for model """
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
