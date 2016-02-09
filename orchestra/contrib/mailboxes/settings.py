import os
import textwrap

from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.settings import Setting
from orchestra.core.validators import validate_name
from orchestra.settings import ORCHESTRA_BASE_DOMAIN


_names = ('name', 'username',)
_backend_names = _names + ('user', 'group', 'home')
mark_safe_lazy = lazy(mark_safe, str)


MAILBOXES_DOMAIN_MODEL = Setting('MAILBOXES_DOMAIN_MODEL', 'domains.Domain',
    validators=[Setting.validate_model_label]
)


MAILBOXES_NAME_MAX_LENGTH = Setting('MAILBOXES_NAME_MAX_LENGTH',
    32,
    help_text=_("Limit for system user based mailbox on Linux is 32.")
)


MAILBOXES_HOME = Setting('MAILBOXES_HOME',
    '/home/%(name)s',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_names),
    validators=[Setting.string_format_validator(_names)],
)


MAILBOXES_SIEVE_PATH = Setting('MAILBOXES_SIEVE_PATH',
    os.path.join('%(home)s/sieve/orchestra.sieve'),
    help_text="If you are using Dovecot you can use "
        "<a href='http://wiki2.dovecot.org/Pigeonhole/Sieve/Configuration#line-130'>"
        "<tt>sieve_before</tt></a> in order to make sure orchestra sieve script is exectued."
        "<br>Available fromat names: <tt>%s</tt>" % ', '.join(_names),
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


MAILBOXES_SPAM_SCORE_HEADER = Setting('MAILBOXES_SPAM_SCORE_HEADER',
    'X-Spam-Score'
)


MAILBOXES_SPAM_SCORE_SYMBOL = Setting('MAILBOXES_SPAM_SCORE_SYMBOL',
    '',
    help_text="Blank for numeric spam score.",
)


MAILBOXES_MAILBOX_FILTERINGS = Setting('MAILBOXES_MAILBOX_FILTERINGS',
    {
        # value: (verbose_name, filter)
        'DISABLE': (_("Disable"), ''),
        'REJECT': (mark_safe_lazy(_("Reject spam (Score&ge;8)")), (
            textwrap.dedent("""\
                if header :contains "%(score_header)s" "%(score_value)s" {
                    discard;
                    stop;
                }""") if MAILBOXES_SPAM_SCORE_SYMBOL else
            textwrap.dedent("""\
                require ["relational","comparator-i;ascii-numeric"];
                if allof (
                   not header :matches "%(score_header)s" "-*",
                   header :value "ge" :comparator "i;ascii-numeric" "%(score_header)s" "8" )
                {
                    discard;
                    stop;
                }""")) % {
                    'score_header': MAILBOXES_SPAM_SCORE_HEADER,
                    'score_value': MAILBOXES_SPAM_SCORE_SYMBOL*8
                }
            ),
        'REJECT5': (mark_safe_lazy(_("Reject spam (Score&ge;5)")), (
            textwrap.dedent("""\
                if header :contains "%(score_header)s" "%(score_value)s" {
                    discard;
                    stop;
                }""") if MAILBOXES_SPAM_SCORE_SYMBOL else
            textwrap.dedent("""\
                require ["relational","comparator-i;ascii-numeric"];
                if allof (
                   not header :matches "%(score_header)s" "-*",
                   header :value "ge" :comparator "i;ascii-numeric" "%(score_header)s" "5" )
                {
                    discard;
                    stop;
                }""")) % {
                    'score_header': MAILBOXES_SPAM_SCORE_HEADER,
                    'score_value': MAILBOXES_SPAM_SCORE_SYMBOL*5
                }
            ),
        'REDIRECT': (mark_safe_lazy(_("Archive spam (Score&ge;8)")), (
            textwrap.dedent("""\
                require "fileinto";
                if header :contains "%(score_header)s" "%(score_value)s" {
                    fileinto "Spam";
                    stop;
                }""") if MAILBOXES_SPAM_SCORE_SYMBOL else
            textwrap.dedent("""\
                require ["fileinto","relational","comparator-i;ascii-numeric"];
                if allof (
                   not header :matches "%(score_header)s" "-*",
                   header :value "ge" :comparator "i;ascii-numeric" "%(score_header)s" "8" )
                {
                    fileinto "Spam";
                    stop;
                }""")) % {
                    'score_header': MAILBOXES_SPAM_SCORE_HEADER,
                    'score_value': MAILBOXES_SPAM_SCORE_SYMBOL*8
                }
            ),
        'REDIRECT5': (mark_safe_lazy(_("Archive spam (Score&ge;5)")), (
            textwrap.dedent("""\
                require "fileinto";
                if header :contains "%(score_header)s" "%(score_value)s" {
                    fileinto "Spam";
                    stop;
                }""") if MAILBOXES_SPAM_SCORE_SYMBOL else
            textwrap.dedent("""\
                require ["fileinto","relational","comparator-i;ascii-numeric"];
                if allof (
                   not header :matches "%(score_header)s" "-*",
                   header :value "ge" :comparator "i;ascii-numeric" "%(score_header)s" "5" )
                {
                    fileinto "Spam";
                    stop;
                }""")) % {
                    'score_header': MAILBOXES_SPAM_SCORE_HEADER,
                    'score_value': MAILBOXES_SPAM_SCORE_SYMBOL*5
                }
            ),
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



MAILBOXES_MAIL_LOG_PATH = Setting('MAILBOXES_MAIL_LOG_PATH',
    '/var/log/mail.log'
)


MAILBOXES_MOVE_ON_DELETE_PATH = Setting('MAILBOXES_MOVE_ON_DELETE_PATH',
    '',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_backend_names),
    validators=[Setting.string_format_validator(_backend_names)],
)
