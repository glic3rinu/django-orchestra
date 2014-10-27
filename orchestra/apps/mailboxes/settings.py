import os
import textwrap

from django.conf import settings
from django.utils.translation import ugettext_lazy as _


MAILBOXES_DOMAIN_MODEL = getattr(settings, 'MAILBOXES_DOMAIN_MODEL', 'domains.Domain')


MAILBOXES_HOME = getattr(settings, 'MAILBOXES_HOME', '/home/%(name)s/')


MAILBOXES_SIEVE_PATH = getattr(settings, 'MAILBOXES_SIEVE_PATH',
        os.path.join(MAILBOXES_HOME, 'Maildir/sieve/orchestra.sieve'))


MAILBOXES_SIEVETEST_PATH = getattr(settings, 'MAILBOXES_SIEVETEST_PATH', '/dev/shm')


MAILBOXES_SIEVETEST_BIN_PATH = getattr(settings, 'MAILBOXES_SIEVETEST_BIN_PATH',
        '%(orchestra_root)s/bin/sieve-test')


MAILBOXES_VIRTUAL_MAILBOX_MAPS_PATH = getattr(settings, 'MAILBOXES_VIRTUAL_MAILBOX_MAPS_PATH',
        '/etc/postfix/virtual_mailboxes')
        

MAILBOXES_VIRTUAL_ALIAS_MAPS_PATH = getattr(settings, 'MAILBOXES_VIRTUAL_ALIAS_MAPS_PATH',
        '/etc/postfix/virtual_aliases')


MAILBOXES_VIRTUAL_ALIAS_DOMAINS_PATH = getattr(settings, 'MAILBOXES_VIRTUAL_ALIAS_DOMAINS_PATH',
        '/etc/postfix/virtual_domains')


MAILBOXES_VIRTUAL_MAILBOX_DEFAULT_DOMAIN = getattr(settings, 'MAILBOXES_VIRTUAL_MAILBOX_DEFAULT_DOMAIN', 
        'orchestra.lan')


MAILBOXES_PASSWD_PATH = getattr(settings, 'MAILBOXES_PASSWD_PATH',
        '/etc/dovecot/passwd')


MAILBOXES_MAILBOX_FILTERINGS = getattr(settings, 'MAILBOXES_MAILBOX_FILTERINGS', {
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


MAILBOXES_MAILBOX_DEFAULT_FILTERING = getattr(settings, 'MAILBOXES_MAILBOX_DEFAULT_FILTERING', 'REDIRECT')
