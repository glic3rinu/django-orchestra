from orchestra.contrib.settings import Setting
from orchestra.core.validators import validate_ipv4_address, validate_ipv6_address, validate_ip_address
from orchestra.settings import ORCHESTRA_BASE_DOMAIN

from .validators import validate_zone_interval, validate_mx_record, validate_domain_name


DOMAINS_DEFAULT_NAME_SERVER = Setting('DOMAINS_DEFAULT_NAME_SERVER',
    'ns.{}'.format(ORCHESTRA_BASE_DOMAIN),
    validators=[validate_domain_name],
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default."
)


DOMAINS_DEFAULT_HOSTMASTER = Setting('DOMAINS_DEFAULT_HOSTMASTER',
    'hostmaster@{}'.format(ORCHESTRA_BASE_DOMAIN),
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default."
)


DOMAINS_DEFAULT_TTL = Setting('DOMAINS_DEFAULT_TTL',
    '1h',
    validators=[validate_zone_interval],
)


DOMAINS_DEFAULT_REFRESH = Setting('DOMAINS_DEFAULT_REFRESH',
    '1d',
    validators=[validate_zone_interval],
)


DOMAINS_DEFAULT_RETRY = Setting('DOMAINS_DEFAULT_RETRY',
    '2h',
    validators=[validate_zone_interval],
)


DOMAINS_DEFAULT_EXPIRE = Setting('DOMAINS_DEFAULT_EXPIRE',
    '4w',
    validators=[validate_zone_interval],
)


DOMAINS_DEFAULT_MIN_TTL = Setting('DOMAINS_DEFAULT_MIN_TTL',
    '1h',
    validators=[validate_zone_interval],
)


DOMAINS_ZONE_PATH = Setting('DOMAINS_ZONE_PATH',
    '/etc/bind/master/%(name)s'
)


DOMAINS_MASTERS_PATH = Setting('DOMAINS_MASTERS_PATH',
    '/etc/bind/named.conf.local',
)


DOMAINS_SLAVES_PATH = Setting('DOMAINS_SLAVES_PATH',
    '/etc/bind/named.conf.local',
)


DOMAINS_CHECKZONE_BIN_PATH = Setting('DOMAINS_CHECKZONE_BIN_PATH',
    'named-checkzone -i local -k fail -n fail',
)


DOMAINS_ZONE_VALIDATION_TMP_DIR = Setting('DOMAINS_ZONE_VALIDATION_TMP_DIR',
    '/dev/shm',
    help_text="Used for creating temporary zone files used for validation."
)


DOMAINS_DEFAULT_A = Setting('DOMAINS_DEFAULT_A',
    '10.0.3.13',
    validators=[validate_ipv4_address]
)


DOMAINS_DEFAULT_AAAA = Setting('DOMAINS_DEFAULT_AAAA', '',
    validators=[validate_ipv6_address]
)


DOMAINS_DEFAULT_MX = Setting('DOMAINS_DEFAULT_MX',
    default=(
        '10 mail.{}.'.format(ORCHESTRA_BASE_DOMAIN),
        '10 mail2.{}.'.format(ORCHESTRA_BASE_DOMAIN),
    ),
    validators=[lambda mxs: list(map(validate_mx_record, mxs))],
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default."
)


DOMAINS_DEFAULT_NS = Setting('DOMAINS_DEFAULT_NS',
    default=(
        'ns1.{}.'.format(ORCHESTRA_BASE_DOMAIN),
        'ns2.{}.'.format(ORCHESTRA_BASE_DOMAIN),
    ),
    validators=[lambda nss: list(map(validate_domain_name, nss))],
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default."
)


DOMAINS_FORBIDDEN = Setting('DOMAINS_FORBIDDEN',
    '',
    help_text=(
        "This setting prevents users from providing random domain names, i.e. google.com<br>"
        "You can generate a 5K forbidden domains list from Alexa's top 1M:<br>"
        "<tt>  wget http://s3.amazonaws.com/alexa-static/top-1m.csv.zip -O /tmp/top-1m.csv.zip && "
        "unzip -p /tmp/top-1m.csv.zip | head -n 5000 | sed 's/^.*,//' > forbidden_domains.list</tt><br>"
        "'%(site_dir)s/forbidden_domains.list')"
   )
)


DOMAINS_MASTERS = Setting('DOMAINS_MASTERS',
    (),
    validators=[lambda masters: list(map(validate_ip_address, masters))],
    help_text="Additional master server ip addresses other than autodiscovered by router.get_servers()."
)

#TODO remove pangea-specific default
DOMAINS_DEFAULT_DNS2136 = "key pangea.key;"
