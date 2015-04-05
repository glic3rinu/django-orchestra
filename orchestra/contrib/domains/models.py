from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.core import services
from orchestra.core.validators import validate_ipv4_address, validate_ipv6_address, validate_ascii
from orchestra.utils.python import AttrDict

from . import settings, validators, utils


class Domain(models.Model):
    name = models.CharField(_("name"), max_length=256, unique=True,
        help_text=_("Domain or subdomain name."),
        validators=[
            validators.validate_domain_name,
            validators.validate_allowed_domain
        ])
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"), blank=True,
        related_name='domains', help_text=_("Automatically selected for subdomains."))
    top = models.ForeignKey('domains.Domain', null=True, related_name='subdomain_set',
        editable=False)
    serial = models.IntegerField(_("serial"), default=utils.generate_zone_serial,
        help_text=_("Serial number"))
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_parent_domain(cls, name, top=False):
        """ get the next domain on the chain """
        split = name.split('.')
        parent = None
        for i in range(1, len(split)-1):
            name = '.'.join(split[i:])
            domain = Domain.objects.filter(name=name)
            if domain:
                parent = domain.get()
                if not top:
                    return parent
        return parent
    
    @property
    def origin(self):
        return self.top or self
    
    @property
    def is_top(self):
        # don't cache, don't replace by top_id
        return not bool(self.top)
    
    @property
    def subdomains(self):
        return Domain.objects.filter(name__regex='\.%s$' % self.name)
    
    def clean(self):
        self.name = self.name.lower()
    
    def save(self, *args, **kwargs):
        """ create top relation """
        update = False
        if not self.pk:
            top = self.get_parent(top=True)
            if top:
                self.top = top
                self.account_id = self.account_id or top.account_id
            else:
                update = True
        super(Domain, self).save(*args, **kwargs)
        if update:
            for domain in self.subdomains.exclude(pk=self.pk):
                # queryset.update() is not used because we want to trigger backend to delete ex-topdomains
                domain.top = self
                domain.save(update_fields=['top'])
    
    def get_description(self):
        if self.is_top:
            num = self.subdomains.count()
            return ungettext(
                _("top domain with one subdomain"),
                _("top domain with %d subdomains") % num,
                num)
        return _("subdomain")
    
    def get_absolute_url(self):
        return 'http://%s' % self.name
    
    def get_records(self):
        """ proxy method, needed for input validation, see helpers.domain_for_validation """
        return self.records.all()
    
    def get_subdomains(self):
        """ proxy method, needed for input validation, see helpers.domain_for_validation """
        return self.origin.subdomain_set.all().prefetch_related('records')
    
    def get_parent(self, top=False):
        return type(self).get_parent_domain(self.name, top=top)
    
    def render_zone(self):
        origin = self.origin
        zone = origin.render_records()
        tail = []
        for subdomain in origin.get_subdomains():
            if subdomain.name.startswith('*'):
                # This subdomains needs to be rendered last in order to avoid undesired matches
                tail.append(subdomain)
            else:
                zone += subdomain.render_records()
        for subdomain in sorted(tail, key=lambda x: len(x.name), reverse=True):
            zone += subdomain.render_records()
        return zone
    
    def refresh_serial(self):
        """ Increases the domain serial number by one """
        serial = utils.generate_zone_serial()
        if serial <= self.serial:
            num = int(str(self.serial)[8:]) + 1
            if num >= 99:
                raise ValueError('No more serial numbers for today')
            serial = str(self.serial)[:8] + '%.2d' % num
            serial = int(serial)
        self.serial = serial
        self.save(update_fields=['serial'])
    
    def render_records(self):
        types = {}
        records = []
        for record in self.get_records():
            types[record.type] = True
            if record.type == record.SOA:
                # Update serial and insert at 0
                value = record.value.split()
                value[2] = str(self.serial)
                records.insert(0, AttrDict(
                    type=record.SOA,
                    ttl=record.get_ttl(),
                    value=' '.join(value)
                ))
            else:
                records.append(AttrDict(
                    type=record.type,
                    ttl=record.get_ttl(),
                    value=record.value
                ))
        if self.is_top:
            if Record.NS not in types:
                for ns in settings.DOMAINS_DEFAULT_NS:
                    records.append(AttrDict(
                        type=Record.NS,
                        value=ns
                    ))
            if Record.SOA not in types:
                soa = [
                    "%s." % settings.DOMAINS_DEFAULT_NAME_SERVER,
                    utils.format_hostmaster(settings.DOMAINS_DEFAULT_HOSTMASTER),
                    str(self.serial),
                    settings.DOMAINS_DEFAULT_REFRESH,
                    settings.DOMAINS_DEFAULT_RETRY,
                    settings.DOMAINS_DEFAULT_EXPIRATION,
                    settings.DOMAINS_DEFAULT_MIN_CACHING_TIME
                ]
                records.insert(0, AttrDict(
                    type=Record.SOA,
                    value=' '.join(soa)
                ))
        is_host = self.is_top or not types or Record.A in types or Record.AAAA in types
        if Record.MX not in types and is_host:
            for mx in settings.DOMAINS_DEFAULT_MX:
                records.append(AttrDict(
                    type=Record.MX,
                    value=mx
                ))
        if (Record.A not in types and Record.AAAA not in types) and is_host:
            records.append(AttrDict(
                type=Record.A,
                value=settings.DOMAINS_DEFAULT_A
            ))
        result = ''
        for record in records:
            name = '{name}.{spaces}'.format(
                name=self.name,
                spaces=' ' * (37-len(self.name))
            )
            ttl = record.get('ttl', settings.DOMAINS_DEFAULT_TTL)
            ttl = '{spaces}{ttl}'.format(
                spaces=' ' * (7-len(ttl)),
                ttl=ttl
            )
            type = '{type} {spaces}'.format(
                type=record.type,
                spaces=' ' * (7-len(record.type))
            )
            result += '{name} {ttl} IN {type} {value}\n'.format(
                name=name,
                ttl=ttl,
                type=type,
                value=record.value
            )
        return result


class Record(models.Model):
    """ Represents a domain resource record  """
    MX = 'MX'
    NS = 'NS'
    CNAME = 'CNAME'
    A = 'A'
    AAAA = 'AAAA'
    SRV = 'SRV'
    TXT = 'TXT'
    SOA = 'SOA'
    
    TYPE_CHOICES = (
        (MX, "MX"),
        (NS, "NS"),
        (CNAME, "CNAME"),
        (A, _("A (IPv4 address)")),
        (AAAA, _("AAAA (IPv6 address)")),
        (SRV, "SRV"),
        (TXT, "TXT"),
        (SOA, "SOA"),
    )
    
    domain = models.ForeignKey(Domain, verbose_name=_("domain"), related_name='records')
    ttl = models.CharField(_("TTL"), max_length=8, blank=True,
        help_text=_("Record TTL, defaults to %s") % settings.DOMAINS_DEFAULT_TTL,
        validators=[validators.validate_zone_interval])
    type = models.CharField(_("type"), max_length=32, choices=TYPE_CHOICES)
    value = models.CharField(_("value"), max_length=256)
    
    def __str__(self):
        return "%s %s IN %s %s" % (self.domain, self.get_ttl(), self.type, self.value)
    
    def clean(self):
        """ validates record value based on its type """
        # validate value
        self.value = self.value.lower().strip()
        choices = {
            self.MX: validators.validate_mx_record,
            self.NS: validators.validate_zone_label,
            self.A: validate_ipv4_address,
            self.AAAA: validate_ipv6_address,
            self.CNAME: validators.validate_zone_label,
            self.TXT: validate_ascii,
            self.SRV: validators.validate_srv_record,
            self.SOA: validators.validate_soa_record,
        }
        try:
            choices[self.type](self.value)
        except ValidationError as error:
            raise ValidationError({'value': error})
    
    def get_ttl(self):
        return self.ttl or settings.DOMAINS_DEFAULT_TTL


services.register(Domain)
