import pkgutil


for __, module_name, __ in pkgutil.walk_packages(__path__):
    exec('from . import %s' % module_name)
