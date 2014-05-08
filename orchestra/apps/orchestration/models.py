from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.utils.apps import autodiscover

from . import settings, manager
from .backends import ServiceBackend


class Server(models.Model):
    """ Machine runing daemons (services) """
    name = models.CharField(_("name"), max_length=256, unique=True)
    # TODO unique address with blank=True (nullablecharfield)
    address = models.CharField(_("address"), max_length=256, blank=True,
            help_text=_("IP address or domain name"))
    description = models.TextField(_("description"), blank=True)
    os = models.CharField(_("operative system"), max_length=32,
            choices=settings.ORCHESTRATION_OS_CHOICES,
            default=settings.ORCHESTRATION_DEFAULT_OS)
    
    def __unicode__(self):
        return self.name
    
    def get_address(self):
        if self.address:
            return self.address
        return self.name


class BackendLog(models.Model):
    RECEIVED = 'RECEIVED'
    TIMEOUT = 'TIMEOUT'
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    ERROR = 'ERROR'
    REVOKED = 'REVOKED'
    
    STATES = (
        (RECEIVED, RECEIVED),
        (TIMEOUT, TIMEOUT),
        (STARTED, STARTED),
        (SUCCESS, SUCCESS),
        (FAILURE, FAILURE),
        (ERROR, ERROR),
        (REVOKED, REVOKED),
    )
    
    backend = models.CharField(_("backend"), max_length=256)
    state = models.CharField(_("state"), max_length=16, choices=STATES,
            default=RECEIVED)
    server = models.ForeignKey(Server, verbose_name=_("server"),
            related_name='execution_logs')
    script = models.TextField(_("script"))
    stdout = models.TextField()
    stderr = models.TextField()
    traceback = models.TextField(_("traceback"))
    exit_code = models.IntegerField(_("exit code"), null=True)
    task_id = models.CharField(_("task ID"), max_length=36, unique=True, null=True,
            help_text="Celery task ID")
    created = models.DateTimeField(_("created"), auto_now_add=True)
    last_update = models.DateTimeField(_("last update"), auto_now=True)
    
    class Meta:
        get_latest_by = 'created'
    
    @property
    def execution_time(self):
        return (self.last_update-self.created).total_seconds()


class BackendOperation(models.Model):
    """
    Encapsulates an operation, storing its related object, the action and the backend.
    """
    SAVE = 'save'
    DELETE = 'delete'
    ACTIONS = (
        (SAVE, _("save")),
        (DELETE, _("delete")),
    )
    
    log = models.ForeignKey('orchestration.BackendLog', related_name='operations')
    backend_class = models.CharField(_("backend"), max_length=256)
    action = models.CharField(_("action"), max_length=64, choices=ACTIONS)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    instance = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        verbose_name = _("Operation")
        verbose_name_plural = _("Operations")
    
    def __unicode__(self):
        return '%s.%s(%s)' % (self.backend_class, self.action, self.instance)
    
    def __hash__(self):
        """ set() """
        backend = getattr(self, 'backend', self.backend_class)
        return hash(backend) + hash(self.instance) + hash(self.action)
    
    def __eq__(self, operation):
        """ set() """
        return hash(self) == hash(operation)
    
    @classmethod
    def create(cls, backend, instance, action):
        op = cls(backend_class=backend.get_name(), instance=instance, action=action)
        op.backend = backend
        return op
    
    @classmethod
    def execute(cls, operations):
        return manager.execute(operations)


autodiscover('backends')


class Route(models.Model):
    """
    Defines the routing that determine in which server a backend is executed
    """
    backend = models.CharField(_("backend"), max_length=256,
            choices=ServiceBackend.get_choices())
    host = models.ForeignKey(Server, verbose_name=_("host"))
    match = models.CharField(_("match"), max_length=256, blank=True, default='True',
            help_text=_("Python expression used for selecting the targe host, "
                        "<em>instance</em> referes to the current object."))
#    async = models.BooleanField(default=False)
#    method = models.CharField(_("method"), max_lenght=32, choices=method_choices,
#            default=MethodBackend.get_default())
    is_active = models.BooleanField(_("is active"), default=True)
    
    class Meta:
        unique_together = ('backend', 'host')
    
    def __unicode__(self):
        return "%s@%s" % (self.backend, self.host)
    
#    def clean(self):
#        backend, method = self.get_backend_class(), self.get_method_class()
#        if not backend.type in method.types:
#            msg = _("%s backend is not compatible with %s method")
#            raise ValidationError(msg % (self.backend, self.method)
    
    @classmethod
    def get_servers(cls, operation):
        backend_name = operation.backend.get_name()
        try:
            routes = cls.objects.filter(is_active=True, backend=backend_name)
        except cls.DoesNotExist:
            return []
        safe_locals = { 'instance': operation.instance }
        pks = [ route.pk for route in routes.all() if eval(route.match, safe_locals) ]
        return [ route.host for route in routes.filter(pk__in=pks) ]
    
    def get_backend(self):
        for backend in ServiceBackend.get_backends():
            if backend.get_name() == self.backend:
                return backend
        raise KeyError('This backend is not registered')
    
#    def get_method_class(self):
#        for method in MethodBackend.get_backends():
#            if method.get_name() == self.method:
#                return method
#        raise ValueError('This method is not registered')
    
    def enable(self):
        self.is_active = True
        self.save()
    
    def disable(self):
        self.is_active = False
        self.save()
