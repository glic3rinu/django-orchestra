from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.orchestration import ServiceBackend
from orchestra.utils import autodiscover


autodiscover('backends')

backend_choices = (
    (backend.name, backend.verbose_name)
        for backend in ServiceBackend.get_backends())


class Daemon(models.Model):
    """ Represents a particular program which provides some service that has to be managed """
    name = models.CharField(_("name"), max_length=256)
    hosts = models.ManyToManyField('orchestration.Server', verbose_name=_("Hosts"),
            through='Instance')
    backend = models.CharField(_("backend"), max_length=256, choices=backend_choices,
            unique=True)
    is_active = models.BooleanField(_("is active"), default=True)
    
    def __unicode__(self):
        return self.name
    
    @classmethod
    def get_servers(cls, operation):
        try:
            daemon = cls.objects.get(is_active=True, backend=operation.backend)
        except cls.DoesNotExist:
            return []
        return [ host for host in daemon.instances.match(operation.obj) ]
    
    def get_backend(self):
        for backend in ServiceBackend.get_backends():
            if backend.name == self.backend:
                return backend
        raise ValueError("This backend is not registered")
    
    def enable(self):
        self.is_active = True
        self.save()
    
    def disable(self):
        self.is_active = False
        self.save()


# TODO rename router
class InstanceManager(models.Manager):
    def match(self, obj):
        """ returns all instances which the router evaluates true """
        safe_locals = { 'obj': obj }
        pks = [ inst.pk for inst in self.all() if eval(inst.router, safe_locals) ]
        return self.filter(pk__in=pks)


class Instance(models.Model):
    """ Represents a daemon running on a particular host """
    daemon = models.ForeignKey(Daemon, verbose_name=_("daemon"),
            related_name='instances')
    host = models.ForeignKey('orchestration.Server', verbose_name=_("host"))
    router = models.CharField(_("router"), max_length=256, blank=True, default='True',
            help_text=_("Python expression used for selecting the targe host"))
    
    objects = InstanceManager()
    
    class Meta:
        unique_together = ('daemon', 'host')
    
    def __unicode__(self):
        return "%s@%s" % (self.daemon, self.host)
