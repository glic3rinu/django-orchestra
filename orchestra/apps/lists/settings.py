from django.conf import settings



LISTS_DOMAIN_MODEL = getattr(settings, 'LISTS_DOMAIN_MODEL', 'domains.Domain')


LISTS_DEFAULT_DOMAIN = getattr(settings, 'LIST_DEFAULT_DOMAIN', 'lists.orchestra.lan')


LISTS_MAILMAN_POST_LOG_PATH = getattr(settings, 'LISTS_MAILMAN_POST_LOG_PATH',
        '/var/log/mailman/post')


LISTS_VIRTUAL_ALIAS_PATH = getattr(settings, 'LISTS_VIRTUAL_ALIAS_PATH',
        '/etc/postfix/mailman_virtual_aliases')


MAILS_VIRTUAL_ALIAS_DOMAINS_PATH = getattr(settings, 'MAILS_VIRTUAL_ALIAS_DOMAINS_PATH',
        '/etc/postfix/mailman_virtual_domains')
