import logging
import textwrap
from functools import partial

from django.apps import apps
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra import plugins

from . import methods

logger = logging.getLogger(__name__)

def replace(context, pattern, repl):
    """ applies replace to all context str values """
    for key, value in context.items():
        if isinstance(value, str):
            context[key] = value.replace(pattern, repl)
    return context


class ServiceMount(plugins.PluginMount):
    def __init__(cls, name, bases, attrs):
        # Make sure backends specify a model attribute
        if not (attrs.get('abstract', False) or name == 'ServiceBackend' or cls.model):
            raise AttributeError("'%s' does not have a defined model attribute." % cls)
        super(ServiceMount, cls).__init__(name, bases, attrs)


class ServiceBackend(plugins.Plugin, metaclass=ServiceMount):
    """
    Service management backend base class
    
    It uses the _unit of work_ design principle, which allows bulk operations to
    be conviniently supported. Each backend generates the configuration for all
    the changes of all modified objects, reloading the daemon just once.
    """
    model = None
    related_models = ()  # ((model, accessor__attribute),)
    script_method = methods.SSH
    script_executable = '/bin/bash'
    function_method = methods.Python
    type = 'task'  # 'sync'
    # Don't wait for the backend to finish before continuing with request/response
    ignore_fields = []
    actions = []
    default_route_match = 'True'
    # Force the backend manager to block in multiple backend executions executing them synchronously
    serialize = False
    doc_settings = None
    # By default backend will not run if actions do not generate insctructions,
    # If your backend uses prepare() or commit() only then you should set force_empty_action_execution = True
    force_empty_action_execution = False
    
    def __str__(self):
        return type(self).__name__
    
    def __init__(self):
        self.head = []
        self.content = []
        self.tail = []
    
    def __getattribute__(self, attr):
        """ Select head, content or tail section depending on the method name """
        IGNORE_ATTRS = (
            'append',
            'cmd_section',
            'head',
            'tail',
            'content',
            'script_method',
            'function_method',
            'set_head',
            'set_tail',
            'set_content',
            'actions',
        )
        if attr == 'prepare':
            self.set_head()
        elif attr == 'commit':
            self.set_tail()
        elif attr not in IGNORE_ATTRS and attr in self.actions:
            self.set_content()
        return super(ServiceBackend, self).__getattribute__(attr)
    
    def set_head(self):
        self.cmd_section = self.head
    
    def set_tail(self):
        self.cmd_section = self.tail
    
    def set_content(self):
        self.cmd_section = self.content
    
    @classmethod
    def get_actions(cls):
        return [ action for action in cls.actions if action in dir(cls) ]
    
    @classmethod
    def get_name(cls):
        return cls.__name__
    
    @classmethod
    def is_main(cls, obj):
        opts = obj._meta
        return cls.model == '%s.%s' % (opts.app_label, opts.object_name)
    
    @classmethod
    def get_related(cls, obj):
        opts = obj._meta
        model = '%s.%s' % (opts.app_label, opts.object_name)
        logger.debug('Model: {}'.format(model))
        for rel_model, field in cls.related_models:
            logger.debug('rel_model: {}'.format(rel_model))
            logger.debug('field: {}'.format(field))
            if rel_model == model:
                related = obj
                for attribute in field.split('__'):
                    related = getattr(related, attribute)
                if type(related).__name__ == 'RelatedManager':
                    return related.all()
                return [related]
        return []
    
    @classmethod
    def get_backends(cls, instance=None, action=None):
        backends = cls.get_plugins()
        included = []
        # Filter for instance or action
        for backend in backends:
            include = True
            if instance:
                opts = instance._meta
                if backend.model != '.'.join((opts.app_label, opts.object_name)):
                    include = False
            if include and action:
                if action not in backend.get_actions():
                    include = False
            if include:
                included.append(backend)
        return included
    
    @classmethod
    def get_backend(cls, name):
        return cls.get(name)
    
    @classmethod
    def model_class(cls):
        return apps.get_model(cls.model)
    
    @property
    def scripts(self):
        """ group commands based on their method """
        if not self.content:
            return []
        scripts = {}
        for method, cmd in self.content:
            scripts[method] = []
        for method, commands in self.head + self.content + self.tail:
            try:
                scripts[method] += commands
            except KeyError:
                pass
        return list(scripts.items())
    
    def get_banner(self):
        now = timezone.localtime(timezone.now())
        time = now.strftime("%h %d, %Y %I:%M:%S %Z")
        return "Generated by Orchestra at %s" % time
    
    def create_log(self, server, **kwargs):
        from .models import BackendLog
        state = BackendLog.RECEIVED
        run = bool(self.scripts) or (self.force_empty_action_execution or bool(self.content))
        if not run:
            state = BackendLog.NOTHING
        using = kwargs.pop('using', None)
        manager = BackendLog.objects
        if using:
            manager = manager.using(using)
        log = manager.create(backend=self.get_name(), state=state, server=server)
        return log
    
    def execute(self, server, async=False, log=None):
        from .models import BackendLog
        if log is None:
            log = self.create_log(server)
        run = log.state != BackendLog.NOTHING
        if run:
            scripts = self.scripts
            for method, commands in scripts:
                method(log, server, commands, async)
                if log.state != BackendLog.SUCCESS:
                    break
        return log
    
    def append(self, *cmd):
        # aggregate commands acording to its execution method
        if isinstance(cmd[0], str):
            method = self.script_method
            cmd = cmd[0]
        else:
            method = self.function_method
            cmd = partial(*cmd)
        if not self.cmd_section or self.cmd_section[-1][0] != method:
            self.cmd_section.append((method, [cmd]))
        else:
            self.cmd_section[-1][1].append(cmd)
    
    def get_context(self, obj):
        return {}
    
    def prepare(self):
        """
        hook for executing something at the beging
        define functions or initialize state
        """
        self.append(textwrap.dedent("""\
            set -e
            set -o pipefail
            exit_code=0""")
        )
    
    def commit(self):
        """
        hook for executing something at the end
        apply the configuration, usually reloading a service
        reloading a service is done in a separated method in order to reload
        the service once in bulk operations
        """
        self.append('exit $exit_code')


class ServiceController(ServiceBackend):
    actions = ('save', 'delete')
    abstract = True
    
    @classmethod
    def get_verbose_name(cls):
        return _("[S] %s") % super(ServiceController, cls).get_verbose_name()
    
    @classmethod
    def get_backends(cls):
        """ filter controller classes """
        backends = super(ServiceController, cls).get_backends()
        return [
            backend for backend in backends if issubclass(backend, ServiceController)
        ]
