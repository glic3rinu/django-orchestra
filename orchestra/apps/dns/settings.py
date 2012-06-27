from django.conf import settings

ugettext = lambda s: s

DNS_DEFAULT_PRIMARY_NS = getattr(settings, 'DNS_DEFAULT_PRIMARY_NS', 'ns1.orchestra.org')

DNS_DEFAULT_HOSTMASTER_EMAIL = getattr(settings, 'DNS_DEFAULT_HOSTMASTER_EMAIL', 'suport.orchestra.org')

# Serial number of this zone file
DNS_DOMAIN_SERIAL = getattr(settings, 'DNS_DOMAIN_SERIAL', 203308)

# Slave refresh
DNS_DOMAIN_SLAVE_REFRESH = getattr(settings, 'DNS_DOMAIN_SLAVE_REFRESH', '1d')

# Slave retry time in case of a problem
DNS_DOMAIN_SLAVE_RETRY = getattr(settings, 'DNS_DOMAIN_SLAVE_RETRY', '2h')

# Slave expiration time
DNS_DOMAIN_SLAVE_EXPIRATION = getattr(settings, 'DNS_DOMAIN_SLAVE_EXPIRATION', '4w')

# Minimum caching time in case of failed lookups
DNS_DOMAIN_MIN_CACHING_TIME = getattr(settings, 'DNS_DOMAIN_MIN_CACHING_TIME', '1h')

# Allowed register type
DNS_REGISTER_CHOICES = getattr(settings, 'DNS_REGISTER_CHOICES', (
    ('MX', ugettext('MX')),
    ('TTL', ugettext('TTL')),
    ('NS', ugettext('NS')),
    ('CNAME', ugettext('CNAME')),
    ('A', ugettext('A: IPv4 Address')),
    ('AAAA', ugettext('AAAA: IPv6 Address')),))

DNS_DEFAULT_DOMAIN_REGISTERS = getattr(settings, 'DNS_DEFAULT_DOMAIN_REGISTERS', [{'type':'NS', 'data': 'ns1.orchestra.org.'},])

DNS_EXTENSIONS = getattr(settings, 'DNS_EXTENSIONS', (('com', 'com'),
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

DNS_DEFAULT_EXTENSION = getattr(settings, 'DNS_DEFAULT_EXTENSION', 'org')

DNS_REGISTER_PROVIDER_CHOICES = getattr(settings, 'DNS_REGISTER_PROVIDER_CHOICES', (('', 'None'),
                                                                            ('gandi', 'Gandi'),))

DNS_DEFAULT_REGISTER_PROVIDER = getattr(settings, 'DNS_DEFAULT_REGISTER_PROVIDER', 'gandi')

DNS_DEFAULT_NAME_SERVERS = getattr(settings, 'DNS_DEFAULT_NAME_SERVERS', [{'hostname':'ns1.orchestra.org', 'ip': ''},])

