from django.core.exceptions import ValidationError


class Plugin(object):
    verbose_name = None
    # Used on select plugin view
    class_verbose_name = None
    icon = None
    change_form = None
    form = None
    serializer = None
    change_readonly_fields = ()
    plugin_field = None
    
    def __init__(self, instance=None):
        # Related model instance of this plugin
        self.instance = instance
        if self.form is None:
            from .forms import PluginForm
            self.form = PluginForm
        super().__init__()
    
    @classmethod
    def get_name(cls):
        return getattr(cls, 'name', cls.__name__)
    
    @classmethod
    def get_plugins(cls):
        return cls.plugins
    
    @classmethod
    def get(cls, name):
        if not hasattr(cls, '_registry'):
            cls._registry = {
                plugin.get_name(): plugin for plugin in cls.get_plugins()
            }
        return cls._registry[name]
    
    @classmethod
    def get_verbose_name(cls):
        # don't evaluate p.verbose_name ugettext_lazy
        verbose = getattr(cls.verbose_name, '_proxy____args', [cls.verbose_name])
        if verbose[0]:
            return cls.verbose_name
        else:
            return cls.get_name()
    
    @classmethod
    def get_choices(cls):
        choices = []
        for plugin in cls.get_plugins():
            verbose = plugin.get_verbose_name()
            choices.append(
                (plugin.get_name(), verbose)
            )
        return sorted(choices, key=lambda e: e[1])
    
    @classmethod
    def get_change_readonly_fields(cls):
        return cls.change_readonly_fields
    
    @classmethod
    def get_class_path(cls):
        return '.'.join((cls.__module__, cls.__name__))
    
    def clean_data(self):
        """ model clean, uses cls.serizlier by default """
        if self.serializer:
            serializer = self.serializer(data=self.instance.data)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)
            return serializer.data
        return {}
    
    def get_directive(self):
        raise NotImplementedError
    
    def get_form(self):
        self.form.plugin = self
        self.form.plugin_field = self.plugin_field
        return self.form
    
    def get_change_form(self):
        form = self.change_form or self.form
        form.plugin = self
        form.plugin_field = self.plugin_field
        return form
    
    def get_serializer(self):
        self.serializer.plugin = self
        return self.serializer


class PluginModelAdapter(Plugin):
    """ Adapter class for using model classes as plugins """
    model = None
    name_field = None
    form = None
    
    def __init__(self, instance=None):
        if self.form is None:
            from .forms import PluginModelAdapterForm
            self.form = PluginModelAdapterForm
        super().__init__(instance)
    
    @classmethod
    def get_plugins(cls):
        plugins = []
        for related_instance in cls.model.objects.filter(is_active=True):
            attributes = {
                'related_instance': related_instance,
                'verbose_name': related_instance.verbose_name
            }
            plugins.append(type('PluginAdapter', (cls,), attributes))
        return plugins
    
    @classmethod
    def get(cls, name):
        # don't cache, since models can change
        for plugin in cls.get_plugins():
            if name == plugin.get_name():
                return plugin
    
    @classmethod
    def get_name(cls):
        return getattr(cls.related_instance, cls.name_field)


class PluginMount(type):
    def __init__(cls, name, bases, attrs):
        if not attrs.get('abstract', False):
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
