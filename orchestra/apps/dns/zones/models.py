from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core.validators import validate_ipv4_address, validate_ipv6_address

from . import settings, validators
from .utils import generate_zone_serial


class Zone(models.Model):
    """
    Represents a DNS zone file
    
    http://en.wikipedia.org/wiki/Zone_file
    """
    name = models.CharField(max_length=255, unique=True,
            validators=[validators.validate_zone_label],)
    name_server = models.CharField(_("name server"), max_length=128,
            default=settings.DNS_ZONE_DEFAULT_NAME_SERVER,
            validators=[validators.validate_zone_label],
            help_text=_("hostname of the primary nameserver that is authoritative "
                        "for this domain"))
    hostmaster = models.EmailField(_("hostmaster"),
            default=settings.DNS_ZONE_DEFAULT_HOSTMASTER,
            help_text=_("email of the person to contact"))
    ttl = models.CharField(_("TTL"), null=True, blank=True, max_length=8,
            default=settings.DNS_ZONE_DEFAULT_TTL,
            validators=[validators.validate_zone_interval],
            help_text=_("default expiration time of all resource records without "
                        "their own TTL value, for example 1h (1 hour)"))
    serial = models.IntegerField(_("serial"), default=generate_zone_serial,
            validators=[validators.validate_zone_serial],
            help_text=_("serial number of this zone file"))
    refresh = models.CharField(_("refresh"), max_length=8,
            default=settings.DNS_ZONE_DEFAULT_REFRESH,
            validators=[validators.validate_zone_interval],
            help_text=_("slave refresh, for example 1d (1 day)"))
    retry = models.CharField(_("retry"), max_length=8,
            default=settings.DNS_ZONE_DEFAULT_RETRY,
            validators=[validators.validate_zone_interval],
            help_text=_("slave retry time in case of a problem, for example 2h (2 hours)"))
    expiration = models.CharField(_("expiration"), max_length=8,
            default=settings.DNS_ZONE_DEFAULT_EXPIRATION,
            validators=[validators.validate_zone_interval],
            help_text=_("slave expiration time, for example 4w (4 weeks)"))
    min_caching_time = models.CharField(_("min caching time"), max_length=8,
            default=settings.DNS_ZONE_DEFAULT_MIN_CACHING_TIME,
            validators=[validators.validate_zone_interval],
            help_text=_("maximum caching time in case of failed lookups, "
                        "for example 1h (1 hour)"))
    
    def __unicode__(self):
        return self.name
    
    def refresh_serial(self, commit=True):
        """ Increases the zone serial number by one """
        serial = generate_zone_serial()
        if serial <= self.serial:
            num = int(str(self.serial)[8:]) + 1
            if num >= 99:
                raise ValueError('No more serial numbers for today')
            serial = str(self.serial)[:8] + '%.2d' % num
            serial = int(serial)
        self.serial = serial
        if commit:
            self.save()
    
    @property
    def formatted_hostmaster(self):
        """
        The DNS encodes the <local-part> as a single label, and encodes the
        <mail-domain> as a domain name.  The single label from the <local-part>
        is prefaced to the domain name from <mail-domain> to form the domain
        name corresponding to the mailbox.  Thus the mailbox HOSTMASTER@SRI-
        NIC.ARPA is mapped into the domain name HOSTMASTER.SRI-NIC.ARPA.  If the
        <local-part> contains dots or other special characters, its
        representation in a master file will require the use of backslash
        quoting to ensure that the domain name is properly encoded.  For
        example, the mailbox Action.domains@ISI.EDU would be represented as
        Action\.domains.ISI.EDU.
        http://www.ietf.org/rfc/rfc1035.txt
        """
        name, domain = self.hostmaster.split('@')
        if '.' in name:
            name = name.replace('.', '\.')
        return "%s.%s" % (name, domain)


class Record(models.Model):
    """ Represents a zone resource record  """
    MX = 'MX'
    NS = 'NS'
    CNAME = 'CNAME'
    A = 'A'
    AAAA = 'AAAA'
    
    TYPE_CHOICES = (
        (MX, "MX"),
        (NS, "NS"),
        (CNAME, "CNAME"),
        (A, _("A (IPv4 address)")),
        (AAAA, _("AAAA (IPv6 address)")),
    )
    zone = models.ForeignKey(Zone, verbose_name=_("zone"), related_name='records')
    name = models.CharField(max_length=256, blank=True,
            validators=[validators.validate_record_name])
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    value = models.CharField(max_length=128)
    
    class Meta:
        unique_together = ('zone', 'name', 'type', 'value')
    
    def __unicode__(self):
        return "%s: %s %s %s" % (self.zone, self.name, self.type, self.value)
    
    def clean(self):
        """ validates record value based on its type """
        super(Record, self).clean()
        mapp = {
            self.MX: validators.validate_mx_record,
            self.NS: validators.validate_zone_label,
            self.A: validate_ipv4_address,
            self.AAAA: validate_ipv6_address,
            self.CNAME: validators.validate_zone_label,
        }
        mapp[self.type](self.value)
