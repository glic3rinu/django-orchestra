from django.conf import settings

from orchestra.settings import BASE_DOMAIN


LISTS_DOMAIN_MODEL = getattr(settings, 'LISTS_DOMAIN_MODEL',
    'domains.Domain'
)


LISTS_DEFAULT_DOMAIN = getattr(settings, 'LIST_DEFAULT_DOMAIN',
    'lists.{}'.format(BASE_DOMAIN)
)


LISTS_LIST_URL = getattr(settings, 'LISTS_LIST_URL',
    'https://lists.{}/mailman/listinfo/%(name)s'.format(BASE_DOMAIN)
)


LISTS_MAILMAN_POST_LOG_PATH = getattr(settings, 'LISTS_MAILMAN_POST_LOG_PATH',
    '/var/log/mailman/post'
)


LISTS_MAILMAN_ROOT_PATH = getattr(settings, 'LISTS_MAILMAN_ROOT_PATH',
    '/var/lib/mailman/'
)


LISTS_VIRTUAL_ALIAS_PATH = getattr(settings, 'LISTS_VIRTUAL_ALIAS_PATH',
    '/etc/postfix/mailman_virtual_aliases'
)


LISTS_VIRTUAL_ALIAS_DOMAINS_PATH = getattr(settings, 'LISTS_VIRTUAL_ALIAS_DOMAINS_PATH',
    '/etc/postfix/mailman_virtual_domains'
)
