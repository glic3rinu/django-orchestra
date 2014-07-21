from .functional import cached


class Plugin(object):
    verbose_name = None
    
    @classmethod
    def get_plugin_name(cls):
        return cls.__name__
    
    @classmethod
    def get_plugins(cls):
        return cls.plugins
    
    @classmethod
    @cached
    def get_plugin(cls, name):
        for plugin in cls.get_plugins():
            if plugin.get_plugin_name() == name:
                return plugin
        raise KeyError('This plugin is not registered')
    
    @classmethod
    def get_plugin_choices(cls):
        plugins = cls.get_plugins()
        choices = []
        for p in plugins:
            # don't evaluate p.verbose_name ugettext_lazy
            verbose = getattr(p.verbose_name, '_proxy____args', [p.verbose_name])
            if verbose[0]:
                verbose = p.verbose_name
            else:
                verbose = p.get_plugin_name()
            choices.append((p.get_plugin_name(), verbose))
        return sorted(choices, key=lambda e: e[0])


class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)
