from django.conf import settings


MAILS_DOMAIN_MODEL = getattr(settings, 'MAILS_DOMAIN_MODEL', 'domains.Domain')


MAILS_HOME = getattr(settings, 'MAILS_HOME', '/home/%(name)s/')


MAILS_SIEVETEST_PATH = getattr(settings, 'MAILS_SIEVETEST_PATH', '/dev/shm')


MAILS_SIEVETEST_BIN_PATH = getattr(settings, 'MAILS_SIEVETEST_BIN_PATH',
        '%(orchestra_root)s/bin/sieve-test')


MAILS_VIRTUSERTABLE_PATH = getattr(settings, 'MAILS_VIRTUSERTABLE_PATH',
        '/etc/postfix/virtusertable')


MAILS_VIRTDOMAINS_PATH = getattr(settings, 'MAILS_VIRTDOMAINS_PATH',
        '/etc/postfix/virtdomains')


MAILS_PASSWD_PATH = getattr(settings, 'MAILS_PASSWD_PATH',
        '/etc/dovecot/virtual_users')


MAILS_DEFAUL_FILTERING = getattr(settings, 'MAILS_DEFAULT_FILTERING',
    'require ["fileinto","regex","envelope","vacation","reject","relational","comparator-i;ascii-numeric"];\n'
    '\n'
    'if header :value "ge" :comparator "i;ascii-numeric" "X-Spam-Score" "5" {\n'
    '    fileinto "Junk";\n'
    '    discard;\n'
    '}'
)
