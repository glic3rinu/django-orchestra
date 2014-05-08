from django.conf import settings


DOMAINS_DEFAULT_NAME_SERVER = getattr(settings, 'DOMAINS_DEFAULT_NAME_SERVER',
        'ns.example.com')

DOMAINS_DEFAULT_HOSTMASTER = getattr(settings, 'DOMAINS_DEFAULT_HOSTMASTER',
        'hostmaster@example.com')

DOMAINS_DEFAULT_TTL = getattr(settings, 'DOMAINS_DEFAULT_TTL', '1h')

DOMAINS_DEFAULT_REFRESH = getattr(settings, 'DOMAINS_DEFAULT_REFRESH', '1d')

DOMAINS_DEFAULT_RETRY = getattr(settings, 'DOMAINS_DEFAULT_RETRY', '2h')

DOMAINS_DEFAULT_EXPIRATION = getattr(settings, 'DOMAINS_DEFAULT_EXPIRATION', '4w')

DOMAINS_DEFAULT_MIN_CACHING_TIME = getattr(settings, 'DOMAINS_DEFAULT_MIN_CACHING_TIME', '1h')

DOMAINS_ZONE_PATH = getattr(settings, 'DOMAINS_ZONE_PATH', '/etc/bind/master/%(name)s')

DOMAINS_MASTERS_PATH = getattr(settings, 'DOMAINS_MASTERS_PATH', '/etc/bind/named.conf.local')

DOMAINS_SLAVES_PATH = getattr(settings, 'DOMAINS_SLAVES_PATH', '/etc/bind/named.conf.local')

DOMAINS_MASTERS = getattr(settings, 'DOMAINS_MASTERS', ['10.0.3.13'])

DOMAINS_CHECKZONE_BIN_PATH = getattr(settings, 'DOMAINS_CHECKZONE_BIN_PATH',
    '/usr/sbin/named-checkzone -i local')

DOMAINS_CHECKZONE_PATH = getattr(settings, 'DOMAINS_CHECKZONE_PATH', '/dev/shm')

DOMAINS_DEFAULT_A = getattr(settings, 'DOMAINS_DEFAULT_A', '10.0.3.13')

DOMAINS_DEFAULT_MX = getattr(settings, 'DOMAINS_DEFAULT_MX', (
    '10 mail.orchestra.lan.',
    '10 mail2.orchestra.lan.',
))

DOMAINS_DEFAULT_NS = getattr(settings, 'DOMAINS_DEFAULT_NS', (
    'ns1.orchestra.lan.',
    'ns2.orchestra.lan.',
))

DOMAINS_FORBIDDEN = getattr(settings, 'DOMAINS_FORBIDDEN',
    # This setting prevents users from providing random domain names, i.e. google.com
    # You can generate a 5K forbidden domains list from Alexa's top 1M
    # wget http://s3.amazonaws.com/alexa-static/top-1m.csv.zip -O /tmp/top-1m.csv.zip
    # unzip -p /tmp/top-1m.csv.zip | head -n 5000 | sed "s/^.*,//" > forbidden_domains.list
    # '%(site_root)s/forbidden_domains.list')
    '')
