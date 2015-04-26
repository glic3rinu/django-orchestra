from django.conf import settings

from orchestra.settings import ORCHESTRA_BASE_DOMAIN, Setting


DOMAINS_DEFAULT_NAME_SERVER = Setting('DOMAINS_DEFAULT_NAME_SERVER',
    'ns.{}'.format(ORCHESTRA_BASE_DOMAIN)
)


DOMAINS_DEFAULT_HOSTMASTER = Setting('DOMAINS_DEFAULT_HOSTMASTER',
    'hostmaster@{}'.format(ORCHESTRA_BASE_DOMAIN)
)


DOMAINS_DEFAULT_TTL = Setting('DOMAINS_DEFAULT_TTL',
    '1h'
)


DOMAINS_DEFAULT_REFRESH = Setting('DOMAINS_DEFAULT_REFRESH',
    '1d'
)


DOMAINS_DEFAULT_RETRY = Setting('DOMAINS_DEFAULT_RETRY',
    '2h'
)


DOMAINS_DEFAULT_EXPIRATION = Setting('DOMAINS_DEFAULT_EXPIRATION',
    '4w'
)


DOMAINS_DEFAULT_MIN_CACHING_TIME = Setting('DOMAINS_DEFAULT_MIN_CACHING_TIME',
    '1h'
)


DOMAINS_ZONE_PATH = Setting('DOMAINS_ZONE_PATH',
    '/etc/bind/master/%(name)s'
)


DOMAINS_MASTERS_PATH = Setting('DOMAINS_MASTERS_PATH',
    '/etc/bind/named.conf.local'
)


DOMAINS_SLAVES_PATH = Setting('DOMAINS_SLAVES_PATH',
    '/etc/bind/named.conf.local'
)


DOMAINS_CHECKZONE_BIN_PATH = Setting('DOMAINS_CHECKZONE_BIN_PATH',
    '/usr/sbin/named-checkzone -i local -k fail -n fail'
)


DOMAINS_ZONE_VALIDATION_TMP_DIR = Setting('DOMAINS_ZONE_VALIDATION_TMP_DIR', '/dev/shm',
    help_text="Used for creating temporary zone files used for validation."
)


DOMAINS_DEFAULT_A = Setting('DOMAINS_DEFAULT_A',
    '10.0.3.13'
)


DOMAINS_DEFAULT_AAAA = Setting('DOMAINS_DEFAULT_AAAA',
    ''
)


DOMAINS_DEFAULT_MX = Setting('DOMAINS_DEFAULT_MX', (
    '10 mail.{}.'.format(ORCHESTRA_BASE_DOMAIN),
    '10 mail2.{}.'.format(ORCHESTRA_BASE_DOMAIN),
))


DOMAINS_DEFAULT_NS = Setting('DOMAINS_DEFAULT_NS', (
    'ns1.{}.'.format(ORCHESTRA_BASE_DOMAIN),
    'ns2.{}.'.format(ORCHESTRA_BASE_DOMAIN),
))


DOMAINS_FORBIDDEN = Setting('DOMAINS_FORBIDDEN', '',
    help_text=(
        "This setting prevents users from providing random domain names, i.e. google.com<br>"
        "You can generate a 5K forbidden domains list from Alexa's top 1M:<br>"
        "<tt>  wget http://s3.amazonaws.com/alexa-static/top-1m.csv.zip -O /tmp/top-1m.csv.zip && "
        "unzip -p /tmp/top-1m.csv.zip | head -n 5000 | sed 's/^.*,//' > forbidden_domains.list</tt><br>"
        "'%(site_dir)s/forbidden_domains.list')"
   )
)


DOMAINS_MASTERS = Setting('DOMAINS_MASTERS', (),
    help_text="Additional master server ip addresses other than autodiscovered by router.get_servers()."
)


DOMAINS_SLAVES = Setting('DOMAINS_SLAVES', (),
    help_text="Additional slave server ip addresses other than autodiscovered by router.get_servers()."
)
