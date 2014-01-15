from django.conf import settings
from django.utils.translation import ugettext_lazy as _


DNS_ZONE_DEFAULT_NAME_SERVER = getattr(settings, 'DNS_ZONE_DEFAULT_NAME_SERVER', 'ns.example.com')

DNS_ZONE_DEFAULT_HOSTMASTER = getattr(settings, 'DNS_ZONE_DEFAULT_HOSTMASTER', 'hostmaster.example.com')

DNS_ZONE_DEFAULT_TTL = getattr(settings, 'DNS_ZONE_DEFAULT_TTL', '1h')

DNS_ZONE_DEFAULT_REFRESH = getattr(settings, 'DNS_ZONE_DEFAULT_REFRESH', '1d')

DNS_ZONE_DEFAULT_RETRY = getattr(settings, 'DNS_ZONE_DEFAULT_RETRY', '2h')

DNS_ZONE_DEFAULT_EXPIRATION = getattr(settings, 'DNS_ZONE_DEFAULT_EXPIRATION', '4w')

DNS_ZONE_DEFAULT_MIN_CACHING_TIME = getattr(settings, 'DNS_ZONE_DEFAULT_MIN_CACHING_TIME', '1h')


DNS_RECORD_TYPE_CHOICES = getattr(settings, 'DNS_RECORD_TYPE_CHOICES', (
    ('MX', "MX"),
    ('NS', "NS"),
    ('CNAME', "CNAME")),
    ('A', _("A: IPv4 Address")),
    ('AAAA', _("AAAA: IPv6 Address")),
))
