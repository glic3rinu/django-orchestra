from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import settings
from .utils import generate_zone_serial


class Domain(models.Model):
    """
    Represents the domain part of a zone file
    
    http://en.wikipedia.org/wiki/Zone_file
    """
    name = models.CharField(max_length=255, unique=True)
    name_server = models.CharField(_("name server"), max_length=128,
            default=settings.DNS_ZONE_DEFAULT_NAME_SERVER,
            help_text=_("hostname of the primary nameserver that is authoritative "
                        "for this domain"),
    hostmaster = models.EmailField(_("hostmaster"),
            default=settings.DNS_ZONE_DEFAULT_HOSTMASTER,
            help_text=_("email of the person to contact"))
    ttl = models.DateField(_("TTL"), null=True, blank=True,
            default=settings.DNS_ZONE_DEFAULT_TTL,
            help_text=_("default expiration time of all resource records without "
                        "their own TTL value, for example 1h (1 hour)"))
    serial = models.IntegerField(_("serial"), default=generate_zone_serial,
            help_text=_("serial number of this zone file"))
    refresh = models.CharField(_("refresh"), max_length=16,
            default=settings.DNS_ZONE_DEFAULT_REFRESH,
            help_text=_("slave refresh, for example 1d (1 day)"))
    retry = models.CharField(_("retry"), max_length=8,
            default=settings.DNS_ZONE_DEFAULT_RETRY,
            help_text=_("slave retry time in case of a problem, for example 2h (2 hours)"))
    expiration = models.CharField(_("expiration"), max_length=8,
            default=settings.DNS_ZONE_DEFAULT_EXPIRATION,
            help_text=_("slave expiration time, for example 4w (4 weeks)"))
    min_caching_time = models.CharField(_("min caching time"), max_length=8,
            default=settings.DNS_ZONE_DEFAULT_MIN_CACHING_TIME,
            help_text=_("maximum caching time in case of failed lookups, "
                        "for example 1h (1 hour)"))
    
    def __unicode__(self):
        return self.name
    
    def refresh_serial(self):
        """ Increases the domain serial number by one """
        serial = generate_zone_serial()
        if serial <= self.serial:
            num = int(str(self.serial[8:])) + 1
            if num > 99:
                raise ValueError("No more serial numbers for today")
            serial = str(self.serial[:8]) + '%.2d' % num
            serial = int(serial)
        self.serial = serial
        self.save()


class Record(models.Model):
    """ Represents a zone file resource record  """
    domain = models.ForeignKey(Domain, verbose_name=_("domain"))
    name = models.CharField(max_length=256, default="@")
    type = models.CharField(max_length=32, choices=settings.DNS_RECORD_TYPE_CHOICES)
    value = models.CharField(max_length=128)
    
    def __unicode__(self):
        return "%s: %s %s %s" % (self.domain, self.name, self.type, self.value)
