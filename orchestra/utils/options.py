from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule


def autodiscover(module):
    """ Auto-discover INSTALLED_APPS module.py """
    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        try: 
            import_module('%s.%s' % (app, module))
        except ImportError:
            # Decide whether to bubble up this error. If the app just
            # doesn't have the module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, module):
                print '%s module caused this error:' % module
                raise
