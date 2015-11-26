from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.settings import Setting


_names = ('user', 'username')
_backend_names = _names + ('group', 'shell', 'mainuser', 'home', 'base_home')


SYSTEMUSERS_SHELLS = Setting('SYSTEMUSERS_SHELLS',
    (
        ('/dev/null', _("No shell, FTP only")),
        ('/bin/rssh', _("No shell, SFTP/RSYNC only")),
        ('/bin/bash', "/bin/bash"),
    ),
    validators=[Setting.validate_choices]
)


SYSTEMUSERS_DEFAULT_SHELL = Setting('SYSTEMUSERS_DEFAULT_SHELL',
    '/dev/null',
    choices=SYSTEMUSERS_SHELLS
)


SYSTEMUSERS_DISABLED_SHELLS = Setting('SYSTEMUSERS_DISABLED_SHELLS',
    default=(
        '/dev/null',
        '/bin/rssh',
    ),
)


SYSTEMUSERS_HOME = Setting('SYSTEMUSERS_HOME',
    '/home/%(user)s',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_names),
    validators=[Setting.string_format_validator(_names)],
)


SYSTEMUSERS_FTP_LOG_PATH = Setting('SYSTEMUSERS_FTP_LOG_PATH',
    '/var/log/vsftpd.log'
)


SYSTEMUSERS_MAIL_LOG_PATH = Setting('SYSTEMUSERS_MAIL_LOG_PATH',
    '/var/log/exim4/mainlog'
)

SYSTEMUSERS_DEFAULT_GROUP_MEMBERS = Setting('SYSTEMUSERS_DEFAULT_GROUP_MEMBERS',
    ('www-data',)
)


SYSTEMUSERS_MOVE_ON_DELETE_PATH = Setting('SYSTEMUSERS_MOVE_ON_DELETE_PATH',
    '',
    help_text="Available fromat names: <tt>%s</tt>" % ', '.join(_backend_names),
    validators=[Setting.string_format_validator(_backend_names)],
)


SYSTEMUSERS_FORBIDDEN_PATHS = Setting('SYSTEMUSERS_FORBIDDEN_PATHS',
    (),
    help_text=("Exlude ACL operations or home locations on provided globs, relative to user's home.<br>"
               "e.g. ('logs', 'logs/apache*', 'webapps')"),
)
