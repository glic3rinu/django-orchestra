from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.orchestration import ServiceBackend
from orchestra.utils import autodiscover


autodiscover('backends')

backend_choices = (
    (backend.name, backend.verbose_name.capitalize())
        for backend in ServiceBackend.get_backends())


class Route(models.Model):
    backend = models.CharField(_("backend"), max_length=256, choices=backend_choices,
            unique=True)
    host = models.ForeignKey('orchestration.Server', verbose_name=_("host"))
    match = models.CharField(_("match"), max_length=256, blank=True, default='True',
            help_text=_("Python expression used for selecting the targe host"))
    is_active = models.BooleanField(_("is active"), default=True)
    
    class Meta:
        unique_together = ('backend', 'host')
    
    def __unicode__(self):
        return "%s@%s" % (self.backend, self.host)
    
    @classmethod
    def get_servers(cls, operation):
        try:
            routes = cls.objects.filter(is_active=True, backend=operation.backend)
        except cls.DoesNotExist:
            return []
        safe_locals = { 'obj': operation.obj }
        pks = [ route.pk for route in routes.all() if eval(route.match, safe_locals) ]
        return [ route.host for route in routes.filter(pk__in=pks) ]
    
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
