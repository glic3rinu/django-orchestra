import logging
import socket

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.module_loading import autodiscover_modules
from django.utils.translation import ugettext_lazy as _

from orchestra.core.validators import validate_ip_address, validate_hostname, OrValidator
from orchestra.models.fields import NullableCharField, MultiSelectField

from . import settings
from .backends import ServiceBackend


logger = logging.getLogger(__name__)


class Server(models.Model):
    """ Machine runing daemons (services) """
    name = models.CharField(_("name"), max_length=256, unique=True,
        help_text=_("Verbose name or hostname of this server."))
    address = NullableCharField(_("address"), max_length=256, blank=True,
        validators=[OrValidator(validate_ip_address, validate_hostname)],
        null=True, unique=True, help_text=_(
            "Optional IP address or domain name. If blank, name field will be used for address resolution.<br>"
            "If the IP address never changes you can set this field and save DNS requests."))
    description = models.TextField(_("description"), blank=True)
    os = models.CharField(_("operative system"), max_length=32,
        choices=settings.ORCHESTRATION_OS_CHOICES,
        default=settings.ORCHESTRATION_DEFAULT_OS)
    
    def __str__(self):
        return self.name or str(self.address)
    
    def get_address(self):
        if self.address:
            return self.address
        return self.name
    
    def get_ip(self):
        address = self.get_address()
        try:
            return validate_ip_address(address)
        except ValidationError:
            return socket.gethostbyname(self.name)
    
    def clean(self):
        self.name = self.name.strip()
        self.address = self.address.strip()
        if self.name and not self.address:
            validate = OrValidator(validate_ip_address, validate_hostname)
            validate_hostname(self.name)
            try:
                validate(self.name)
            except ValidationError as err:
                raise ValidationError({
                    'name': _("Name should be a valid hostname or IP address when address is not provided.")
                })


class BackendLog(models.Model):
    RECEIVED = 'RECEIVED'
    TIMEOUT = 'TIMEOUT'
    STARTED = 'STARTED'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    ERROR = 'ERROR'
    REVOKED = 'REVOKED'
    ABORTED = 'ABORTED'
    NOTHING = 'NOTHING'
    # Special state for mocked backendlogs
    EXCEPTION = 'EXCEPTION'
    
    STATES = (
        (RECEIVED, RECEIVED),
        (TIMEOUT, TIMEOUT),
        (STARTED, STARTED),
        (SUCCESS, SUCCESS),
        (FAILURE, FAILURE),
        (ERROR, ERROR),
        (ABORTED, ABORTED),
        (REVOKED, REVOKED),
        (NOTHING, NOTHING),
    )
    
    backend = models.CharField(_("backend"), max_length=256)
    state = models.CharField(_("state"), max_length=16, choices=STATES, default=RECEIVED)
    server = models.ForeignKey(Server, verbose_name=_("server"), related_name='execution_logs')
    script = models.TextField(_("script"))
    stdout = models.TextField(_("stdout"))
    stderr = models.TextField(_("stderr"))
    traceback = models.TextField(_("traceback"))
    exit_code = models.IntegerField(_("exit code"), null=True)
    task_id = models.CharField(_("task ID"), max_length=36, unique=True, null=True,
        help_text="Celery task ID when used as execution backend")
    created_at = models.DateTimeField(_("created"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("updated"), auto_now=True)
    
    class Meta:
        get_latest_by = 'id'
    
    def __str__(self):
        return "%s@%s" % (self.backend, self.server)
    
    @property
    def execution_time(self):
        return (self.updated_at-self.created_at).total_seconds()
    
    @property
    def has_finished(self):
        return self.state not in (self.STARTED, self.RECEIVED)
    
    @property
    def is_success(self):
        return self.state in (self.SUCCESS, self.NOTHING)
    
    def backend_class(self):
        return ServiceBackend.get_backend(self.backend)


class BackendOperationQuerySet(models.QuerySet):
    def create(self, **kwargs):
        instance = kwargs.get('instance')
        if instance and 'instance_repr' not in kwargs:
            kwargs['instance_repr'] = force_text(instance)[:256]
        return super(BackendOperationQuerySet, self).create(**kwargs)


class BackendOperation(models.Model):
    """
    Encapsulates an operation, storing its related object, the action and the backend.
    """
    log = models.ForeignKey('orchestration.BackendLog', related_name='operations')
    backend = models.CharField(_("backend"), max_length=256)
    action = models.CharField(_("action"), max_length=64)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    instance_repr = models.CharField(_("instance representation"), max_length=256)
    
    instance = GenericForeignKey('content_type', 'object_id')
    objects = BackendOperationQuerySet.as_manager()
    
    class Meta:
        verbose_name = _("Operation")
        verbose_name_plural = _("Operations")
        index_together = (
            ('content_type', 'object_id'),
        )
    
    def __str__(self):
        return '%s.%s(%s)' % (self.backend, self.action, self.instance or self.instance_repr)
    
    @cached_property
    def backend_class(self):
        return ServiceBackend.get_backend(self.backend)


autodiscover_modules('backends')


class RouteQuerySet(models.QuerySet):
    def get_for_operation(self, operation, **kwargs):
        cache = kwargs.get('cache', {})
        if not cache:
            for route in self.filter(is_active=True).select_related('host'):
                try:
                    backend_class = route.backend_class
                except KeyError:
                    logger.warning("Backed '%s' not installed." % route.backend)
                else:
                    for action in backend_class.get_actions():
                        key = (route.backend, action)
                        try:
                            cache[key].append(route)
                        except KeyError:
                            cache[key] = [route]
        routes = []
        backend_cls = operation.backend
        key = (backend_cls.get_name(), operation.action)
        try:
            target_routes = cache[key]
        except KeyError:
            pass
        else:
            for route in target_routes:
                if route.matches(operation.instance):
                    routes.append(route)
        return routes


class Route(models.Model):
    """
    Defines the routing that determine in which server a backend is executed
    """
    backend = models.CharField(_("backend"), max_length=256,
        choices=ServiceBackend.get_choices())
    host = models.ForeignKey(Server, verbose_name=_("host"), related_name='routes')
    match = models.CharField(_("match"), max_length=256, blank=True, default='True',
        help_text=_("Python expression used for selecting the targe host, "
                    "<em>instance</em> referes to the current object."))
    async = models.BooleanField(default=False,
        help_text=_("Whether or not block the request/response cycle waitting this backend to "
                    "finish its execution. Usually you want slave servers to run asynchronously."))
    async_actions = MultiSelectField(max_length=256, blank=True,
        help_text=_("Specify individual actions to be executed asynchronoulsy."))
#    method = models.CharField(_("method"), max_lenght=32, choices=method_choices,
#            default=MethodBackend.get_default())
    is_active = models.BooleanField(_("active"), default=True)
    
    objects = RouteQuerySet.as_manager()
    
    class Meta:
        unique_together = ('backend', 'host')
    
    def __str__(self):
        return "%s@%s" % (self.backend, self.host)
    
    @cached_property
    def backend_class(self):
        return ServiceBackend.get_backend(self.backend)
    
    def clean(self):
        if not self.match:
            self.match = 'True'
        if self.backend:
            try:
                backend_class = self.backend_class
            except KeyError:
                raise ValidationError({
                    'backend': _("Backend '%s' is not installed.") % self.backend
                })
            backend_model = backend_class.model_class()
            try:
                obj = backend_model.objects.all()[0]
            except IndexError:
                return
            try:
                bool(self.matches(obj))
            except Exception as exception:
                name = type(exception).__name__
                raise ValidationError(': '.join((name, str(exception))))
    
    def action_is_async(self, action):
        return action in self.async_actions
    
    def matches(self, instance):
        safe_locals = {
            'instance': instance,
            'obj': instance,
            instance._meta.model_name: instance,
        }
        return eval(self.match, safe_locals)
    
    def enable(self):
        self.is_active = True
        self.save()
    
    def disable(self):
        self.is_active = False
        self.save()
