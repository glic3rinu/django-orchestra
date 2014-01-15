from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import settings


class Daemon(models.Model):
    """ Represents a particular program which provides some service that has to be managed """
    name = models.CharField(_("name"), max_length=256)
    hosts = models.ManyToManyField('host', through='Instance', verbose_name=_("Hosts"))
    # TODO scripts (sync or setp based daemon managemente)
    is_active = models.BooleanField(_("is active"), default=True)
    
    def __unicode__(self):
        return self.name


class Host(models.Model):
    """ Machine runing daemons (services) """
    name = models.CharField(_("name"), max_length=256, unique=True)
    # TODO unique address with blank=True (nullablecharfield)
    address = models.CharField(_("address"), max_length=256, blank=True,
            help_text=_("IP address or domain name"))
    description = models.TextField(_("description"), blank=True)
    os = models.CharField(_("operative system"), max_length=32,
            choices=settings.DAEMONS_OS_CHOICES, default=settings.DAEMONS_DEFAULT_OS)
    
    def __unicode__(self):
        return self.name


class Instance(models.Model):
    """ Represents a daemon running on a particular host """
    daemon = models.ForeignKey(Daemon, verbose_name=_("daemon"))
    host = models.ForeignKey(Host, verbose_name=_("host"))
    router = models.CharField(_("router"), max_length=256, blank=True,
            help_text=_("Python expression used for selecting the targe host"))

    class Meta:
        unique_together = ('daemon', 'host')
