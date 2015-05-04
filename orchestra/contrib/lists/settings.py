from orchestra.contrib.settings import Setting
from orchestra.settings import ORCHESTRA_BASE_DOMAIN


LISTS_DOMAIN_MODEL = Setting('LISTS_DOMAIN_MODEL',
    'domains.Domain',
    validators=[Setting.validate_model_label]
)


LISTS_DEFAULT_DOMAIN = Setting('LISTS_DEFAULT_DOMAIN',
    'lists.{}'.format(ORCHESTRA_BASE_DOMAIN),
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default."
)


LISTS_LIST_URL = Setting('LISTS_LIST_URL',
    'https://lists.{}/mailman/listinfo/%(name)s'.format(ORCHESTRA_BASE_DOMAIN),
    help_text="Uses <tt>ORCHESTRA_BASE_DOMAIN</tt> by default."
)


LISTS_MAILMAN_POST_LOG_PATH = Setting('LISTS_MAILMAN_POST_LOG_PATH',
    '/var/log/mailman/post'
)


LISTS_MAILMAN_ROOT_DIR = Setting('LISTS_MAILMAN_ROOT_DIR',
    '/var/lib/mailman'
)


LISTS_VIRTUAL_ALIAS_PATH = Setting('LISTS_VIRTUAL_ALIAS_PATH',
    '/etc/postfix/mailman_virtual_aliases'
)


LISTS_VIRTUAL_ALIAS_DOMAINS_PATH = Setting('LISTS_VIRTUAL_ALIAS_DOMAINS_PATH',
    '/etc/postfix/mailman_virtual_domains'
)
