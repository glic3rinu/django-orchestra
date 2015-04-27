import os
import textwrap

from django.utils.translation import ugettext_lazy as _

from orchestra.core.validators import validate_name
from orchestra.settings import ORCHESTRA_BASE_DOMAIN, Setting


MAILBOXES_DOMAIN_MODEL = Setting('MAILBOXES_DOMAIN_MODEL', 'domains.Domain',
    validators=[Setting.validate_model_label]
)


MAILBOXES_HOME = Setting('MAILBOXES_HOME', '/home/%(name)s/')


MAILBOXES_SIEVE_PATH = Setting('MAILBOXES_SIEVE_PATH',
    os.path.join(MAILBOXES_HOME, 'Maildir/sieve/orchestra.sieve')
)


MAILBOXES_SIEVETEST_PATH = Setting('MAILBOXES_SIEVETEST_PATH', '/dev/shm')


MAILBOXES_SIEVETEST_BIN_PATH = Setting('MAILBOXES_SIEVETEST_BIN_PATH', '%(orchestra_root)s/bin/sieve-test',
    validators=[Setting.string_format_validator(('orchestra_root',))]
)


MAILBOXES_VIRTUAL_MAILBOX_MAPS_PATH = Setting('MAILBOXES_VIRTUAL_MAILBOX_MAPS_PATH',
    '/etc/postfix/virtual_mailboxes'
)


MAILBOXES_VIRTUAL_ALIAS_MAPS_PATH = Setting('MAILBOXES_VIRTUAL_ALIAS_MAPS_PATH',
    '/etc/postfix/virtual_aliases'
)


MAILBOXES_VIRTUAL_ALIAS_DOMAINS_PATH = Setting('MAILBOXES_VIRTUAL_ALIAS_DOMAINS_PATH',
    '/etc/postfix/virtual_domains'
)


MAILBOXES_LOCAL_DOMAIN = Setting('MAILBOXES_LOCAL_DOMAIN', ORCHESTRA_BASE_DOMAIN,
    validators=[validate_name]
)


MAILBOXES_PASSWD_PATH = Setting('MAILBOXES_PASSWD_PATH', '/etc/dovecot/passwd')


MAILBOXES_MAILBOX_FILTERINGS = Setting('MAILBOXES_MAILBOX_FILTERINGS', {
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


MAILBOXES_MAILBOX_DEFAULT_FILTERING = Setting('MAILBOXES_MAILBOX_DEFAULT_FILTERING', 'REDIRECT',
    choices=tuple((k, v[0]) for k,v in MAILBOXES_MAILBOX_FILTERINGS.items())
)


MAILBOXES_MAILDIRSIZE_PATH = Setting('MAILBOXES_MAILDIRSIZE_PATH', '%(home)s/Maildir/maildirsize')


MAILBOXES_LOCAL_ADDRESS_DOMAIN = Setting('MAILBOXES_LOCAL_ADDRESS_DOMAIN', ORCHESTRA_BASE_DOMAIN,
    validators=[validate_name]
)


MAILBOXES_MAIL_LOG_PATH = Setting('MAILBOXES_MAIL_LOG_PATH', '/var/log/mail.log')


MAILBOXES_MOVE_ON_DELETE_PATH = Setting('MAILBOXES_MOVE_ON_DELETE_PATH', '')
