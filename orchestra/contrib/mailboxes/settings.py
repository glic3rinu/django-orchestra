import os
import textwrap

from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.core.validators import validate_name
from orchestra.settings import ORCHESTRA_BASE_DOMAIN, Setting


_names = ('name', 'username',)
_backend_names = _names + ('user', 'group', 'home')
mark_safe_lazy = lazy(mark_safe, str)


MAILBOXES_DOMAIN_MODEL = Setting('MAILBOXES_DOMAIN_MODEL', 'domains.Domain',
    validators=[Setting.validate_model_label]
)


MAILBOXES_HOME = Setting('MAILBOXES_HOME',
    '/home/%(name)s',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_names),
    validators=[Setting.string_format_validator(_names)],
)


MAILBOXES_SIEVE_PATH = Setting('MAILBOXES_SIEVE_PATH',
    os.path.join('%(home)s/Maildir/sieve/orchestra.sieve'),
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_names),
    validators=[Setting.string_format_validator(_backend_names)],
)


MAILBOXES_SIEVETEST_PATH = Setting('MAILBOXES_SIEVETEST_PATH',
    '/dev/shm'
)


MAILBOXES_SIEVETEST_BIN_PATH = Setting('MAILBOXES_SIEVETEST_BIN_PATH',
    '%(orchestra_root)s/bin/sieve-test',
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


MAILBOXES_LOCAL_DOMAIN = Setting('MAILBOXES_LOCAL_DOMAIN',
    ORCHESTRA_BASE_DOMAIN,
    validators=[validate_name],
    help_text="Defaults to <tt>ORCHESTRA_BASE_DOMAIN</tt>."
)


MAILBOXES_PASSWD_PATH = Setting('MAILBOXES_PASSWD_PATH',
    '/etc/dovecot/passwd'
)


MAILBOXES_MAILBOX_FILTERINGS = Setting('MAILBOXES_MAILBOX_FILTERINGS',
    {
        # value: (verbose_name, filter)
        'DISABLE': (_("Disable"), ''),
        'REJECT': (mark_safe_lazy(_("Reject spam (X-Spam-Score&ge;9)")), textwrap.dedent("""
             require ["fileinto","regex","envelope","vacation","reject","relational","comparator-i;ascii-numeric"];
             if header :value "ge" :comparator "i;ascii-numeric" "X-Spam-Score" "9" {
                discard;
                stop;
            }""")),
        'REDIRECT': (mark_safe_lazy(_("Archive spam (X-Spam-Score&ge;9)")), textwrap.dedent("""
            require ["fileinto","regex","envelope","vacation","reject","relational","comparator-i;ascii-numeric"];
            if header :value "ge" :comparator "i;ascii-numeric" "X-Spam-Score" "9" {
                fileinto "Spam";
                stop;
            }""")),
        'CUSTOM': (_("Custom filtering"), lambda mailbox: mailbox.custom_filtering),
    }
)


MAILBOXES_MAILBOX_DEFAULT_FILTERING = Setting('MAILBOXES_MAILBOX_DEFAULT_FILTERING',
    'REDIRECT',
    choices=tuple((k, v[0]) for k,v in MAILBOXES_MAILBOX_FILTERINGS.items())
)


MAILBOXES_MAILDIRSIZE_PATH = Setting('MAILBOXES_MAILDIRSIZE_PATH',
    '%(home)s/Maildir/maildirsize',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_backend_names),
    validators=[Setting.string_format_validator(_backend_names)],
)


MAILBOXES_LOCAL_ADDRESS_DOMAIN = Setting('MAILBOXES_LOCAL_ADDRESS_DOMAIN',
    ORCHESTRA_BASE_DOMAIN,
    validators=[validate_name],
    help_text="Defaults to <tt>ORCHESTRA_BASE_DOMAIN</tt>."
)


MAILBOXES_MAIL_LOG_PATH = Setting('MAILBOXES_MAIL_LOG_PATH',
    '/var/log/mail.log'
)


MAILBOXES_MOVE_ON_DELETE_PATH = Setting('MAILBOXES_MOVE_ON_DELETE_PATH',
    '',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_backend_names),
    validators=[Setting.string_format_validator(_backend_names)],
)
