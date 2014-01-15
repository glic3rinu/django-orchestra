from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import settings


class Web(models.Model):
    """ Represents the web server configuration of a particular web site """
    ip = models.GenericIPAddressField(_("IP"), choices=settings.WEBS_IP_CHOICES,
            default=settings.WEB_DEFAULT_IP)
    port = models.PositiveIntegerField(_("port"), choices=settings.WEBS_PORT_CHOICES,
            default=settings.WEBS_DEFAULT_PORT)
    names = models.ManyToManyField(settings.WEBS_DOMAIN_MODEL, verbose_name=_("Domains"))
    root = models.CharField(_("root"), max_length=256, blank=True,
            default=settings.WEBS_DEFAULT_ROOT)
    directives = models.TextField(blank=True, help_text=_("Custom fields in template "
            "format that will be appended on the web configuration"))
    
    def __unicode__(self):
        return self.name
    
    @property
    def name(self):
        return self.names[0]
