from django.db import models
from django.db.models import Q
import settings

class Zone(models.Model):
    origin = models.CharField(max_length=255)
    primary_ns = models.CharField(max_length=255, default=settings.DNS_DEFAULT_PRIMARY_NS)
    hostmaster_email = models.CharField(max_length=255, default=settings.DNS_DEFAULT_HOSTMASTER_EMAIL)

    expire = models.DateField(null=True, blank=True)
    serial = models.IntegerField(default=settings.DNS_DOMAIN_SERIAL)
    slave_refresh = models.CharField(default=settings.DNS_DOMAIN_SLAVE_REFRESH, max_length=16)
    slave_retry = models.CharField(default=settings.DNS_DOMAIN_SLAVE_RETRY, max_length=8)
    slave_expiration = models.CharField(default=settings.DNS_DOMAIN_SLAVE_EXPIRATION, max_length=8)
    min_caching_time = models.CharField(default=settings.DNS_DOMAIN_MIN_CACHING_TIME, max_length=8)

    # TODO: create a virtual relation with name in order to deprecate the signal approach of auto deletions.

    def __unicode__(self):
        return str(self.origin)

    def get_names(self):
        names = [self.origin]
        for record in self.record_set.filter(Q(Q(type='CNAME') | Q(type='A')) & Q(name__gt='')):
            names.append("%s.%s" % (record.name, self.origin))
        return names


class Record(models.Model):
    """ Domain Record """
    zone = models.ForeignKey(Zone)
    name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=6, choices=settings.DNS_REGISTER_CHOICES)
    data = models.CharField(max_length=128)
    
    def __unicode__(self):
        return "%s.%s-%s.%s" % (self.zone, self.name, self.type, self.data)

