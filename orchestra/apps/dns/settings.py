from django.conf import settings

ugettext = lambda s: s

DEFAULT_PRIMARY_NS = getattr(settings, 'DEFAULT_PRIMARY_NS', 'ns1.orchestra.org')

DEFAULT_HOSTMASTER_EMAIL = getattr(settings, 'DEFAULT_HOSTMASTER_EMAIL', 'suport.orchestra.org')

# Serial number of this zone file
DOMAIN_SERIAL = getattr(settings, 'DOMAIN_SERIAL', 203308)

# Slave refresh
DOMAIN_SLAVE_REFRESH = getattr(settings, 'DOMAIN_SLAVE_REFRESH', '1d')

# Slave retry time in case of a problem
DOMAIN_SLAVE_RETRY = getattr(settings, 'DOMAIN_SLAVE_RETRY', '2h')

# Slave expiration time
DOMAIN_SLAVE_EXPIRATION = getattr(settings, 'DOMAIN_SLAVE_EXPIRATION', '4w')

# Minimum caching time in case of failed lookups
DOMAIN_MIN_CACHING_TIME = getattr(settings, 'DOMAIN_MIN_CACHING_TIME', '1h')

# Allowed register type
REGISTER_CHOICES = getattr(settings, 'REGISTER_CHOICES', (
    ('MX', ugettext('MX')),
    ('TTL', ugettext('TTL')),
    ('NS', ugettext('NS')),
    ('CNAME', ugettext('CNAME')),
    ('A', ugettext('A: IPv4 Address')),
    ('AAAA', ugettext('AAAA: IPv6 Address')),))

DEFAULT_DOMAIN_REGISTERS = getattr(settings, 'DEFAULT_DOMAIN_REGISTERS', [{'type':'NS', 'data': 'ns1.orchestra.org.'},])

EXTENSIONS = getattr(settings, 'EXTENSIONS', (('com', 'com'),
                                              ('org', 'org'),
                                              ('edu', 'edu'),
                                              ('gov', 'gov'),
                                              ('uk', 'uk'),
                                              ('net', 'net'),
                                              ('ca', 'ca'),
                                              ('de', 'de'),
                                              ('jp', 'jp'),
                                              ('fr', 'fr'),
                                              ('au', 'au'),
                                              ('us', 'us'),
                                              ('ru', 'ru'),
                                              ('ch', 'ch'),
                                              ('it', 'it'),
                                              ('nl', 'nl'),
                                              ('se', 'se'),
                                              ('no', 'no'),
                                              ('es', 'es'),))

DEFAULT_EXTENSION = getattr(settings, 'DEFAULT_EXTENSION', 'org')

REGISTER_PROVIDER_CHOICES = getattr(settings, 'REGISTER_PROVIDER_CHOICES', (('', 'None'),
                                                                            ('gandi', 'Gandi'),))

DEFAULT_REGISTER_PROVIDER = getattr(settings, 'DEFAULT_REGISTER_PROVIDER', 'gandi')

DEFAULT_NAME_SERVERS = getattr(settings, 'DEFAULT_NAME_SERVERS', [{'hostname':'ns1.orchestra.org', 'ip': ''},])

