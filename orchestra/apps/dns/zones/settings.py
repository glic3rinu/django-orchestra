from django.conf import settings
from django.utils.translation import ugettext_lazy as _


DNS_ZONE_DEFAULT_NAME_SERVER = getattr(settings, 'DNS_ZONE_DEFAULT_NAME_SERVER', 'ns.example.com')

DNS_ZONE_DEFAULT_HOSTMASTER = getattr(settings, 'DNS_ZONE_DEFAULT_HOSTMASTER', 'hostmaster@example.com')

DNS_ZONE_DEFAULT_TTL = getattr(settings, 'DNS_ZONE_DEFAULT_TTL', '1h')

DNS_ZONE_DEFAULT_REFRESH = getattr(settings, 'DNS_ZONE_DEFAULT_REFRESH', '1d')

DNS_ZONE_DEFAULT_RETRY = getattr(settings, 'DNS_ZONE_DEFAULT_RETRY', '2h')

DNS_ZONE_DEFAULT_EXPIRATION = getattr(settings, 'DNS_ZONE_DEFAULT_EXPIRATION', '4w')

DNS_ZONE_DEFAULT_MIN_CACHING_TIME = getattr(settings, 'DNS_ZONE_DEFAULT_MIN_CACHING_TIME', '1h')


DNS_ZONE_DEFAULT_RECORDS = getattr(settings, 'DNS_DEFAULT_RECORDS', (
    ('', 'NS', 'ns1.orchestra.lan.'),
    ('', 'NS', 'ns2.orchestra.lan.'),
    ('', 'MX', '10 mail.orchestra.lan'),
    ('', 'MX', '20 mail2.orchestra.lan'),
))


DNS_ZONE_FILE_PATH = getattr(settings, 'DNS_ZONE_FILE_PATH', '/etc/bind/master')

DNS_ZONE_MASTER_PATH = getattr(settings, 'DNS_ZONE_MASTER_PATH', '/etc/bind/named.conf.local')
