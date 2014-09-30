from django.conf import settings


EMAILS_DOMAIN_MODEL = getattr(settings, 'EMAILS_DOMAIN_MODEL', 'domains.Domain')

EMAILS_HOME = getattr(settings, 'EMAILS_HOME', '/home/%(username)s/')

EMAILS_SIEVETEST_PATH = getattr(settings, 'EMAILS_SIEVETEST_PATH', '/dev/shm')

EMAILS_SIEVETEST_BIN_PATH = getattr(settings, 'EMAILS_SIEVETEST_BIN_PATH',
        '%(orchestra_root)s/bin/sieve-test')


EMAILS_VIRTUSERTABLE_PATH = getattr(settings, 'EMAILS_VIRTUSERTABLE_PATH',
        '/etc/postfix/virtusertable')


EMAILS_VIRTDOMAINS_PATH = getattr(settings, 'EMAILS_VIRTDOMAINS_PATH',
        '/etc/postfix/virtdomains')


EMAILS_DEFAUL_FILTERING = getattr(settings, 'EMAILS_DEFAULT_FILTERING',
    'require ["fileinto","regex","envelope","vacation","reject","relational","comparator-i;ascii-numeric"];\n'
    '\n'
    'if header :value "ge" :comparator "i;ascii-numeric" "X-Spam-Score" "5" {\n'
    '    fileinto "Junk";\n'
    '    discard;\n'
    '}'
)
