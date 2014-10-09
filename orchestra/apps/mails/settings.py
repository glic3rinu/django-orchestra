import textwrap

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


MAILS_DOMAIN_MODEL = getattr(settings, 'MAILS_DOMAIN_MODEL', 'domains.Domain')


MAILS_HOME = getattr(settings, 'MAILS_HOME', '/home/%(name)s/')


MAILS_SIEVETEST_PATH = getattr(settings, 'MAILS_SIEVETEST_PATH', '/dev/shm')


MAILS_SIEVETEST_BIN_PATH = getattr(settings, 'MAILS_SIEVETEST_BIN_PATH',
        '%(orchestra_root)s/bin/sieve-test')


MAILS_VIRTUAL_MAILBOX_MAPS_PATH = getattr(settings, 'MAILS_VIRTUAL_MAILBOX_MAPS_PATH',
        '/etc/postfix/virtual_mailboxes')
        

MAILS_VIRTUAL_ALIAS_MAPS_PATH = getattr(settings, 'MAILS_VIRTUAL_ALIAS_MAPS_PATH',
        '/etc/postfix/virtual_aliases')


MAILS_VIRTUAL_ALIAS_DOMAINS_PATH = getattr(settings, 'MAILS_VIRTUAL_ALIAS_DOMAINS_PATH',
        '/etc/postfix/virtual_domains')


MAILS_VIRTUAL_MAILBOX_DEFAULT_DOMAIN = getattr(settings, 'MAILS_VIRTUAL_MAILBOX_DEFAULT_DOMAIN', 
        'orchestra.lan')

MAILS_PASSWD_PATH = getattr(settings, 'MAILS_PASSWD_PATH',
        '/etc/dovecot/passwd')



MAILS_MAILBOX_FILTERINGS = getattr(settings, 'MAILS_MAILBOX_FILTERINGS', {
    # value: (verbose_name, filter)
    'DISABLE': (_("Disable"), ''),
    'REJECT': (_("Reject spam"), textwrap.dedent("""
         require ["fileinto","regex","envelope","vacation","reject","relational","comparator-i;ascii-numeric"];
         if header :value "ge" :comparator "i;ascii-numeric" "X-Spam-Score" "5" {
            discard;
            stop;
        }""")),
    'REDIRECT': (_("Archive spam"), textwrap.dedent("""
        require ["fileinto","regex","envelope","vacation","reject","relational","comparator-i;ascii-numeric"];
        if header :value "ge" :comparator "i;ascii-numeric" "X-Spam-Score" "5" {
            fileinto "Spam";
            stop;
        }""")),
    'CUSTOM': (_("Custom filtering"), lambda mailbox: mailbox.custom_filtering),
})


MAILS_MAILBOX_DEFAULT_FILTERING = getattr(settings, 'MAILS_MAILBOX_DEFAULT_FILTERING', 'REDIRECT')
