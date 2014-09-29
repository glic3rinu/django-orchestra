from django.conf import settings

from django.utils.translation import ugettext, ugettext_lazy as _


USERS_SYSTEMUSER_HOME = getattr(settings, 'USERES_SYSTEMUSER_HOME', '/home/%(username)s')

USERS_FTP_LOG_PATH = getattr(settings, 'USERS_FTP_LOG_PATH', '/var/log/vsftpd.log')

USERS_SHELLS = getattr(settings, 'USERS_SHELLS', (
    ('/bin/false', _("FTP/sFTP only")),
    ('/bin/rsync', _("rsync shell")),
    ('/bin/bash', "Bash"),
))

USERS_DEFAULT_SHELL = getattr(settings, 'USERS_DEFAULT_SHELL', '/bin/false')
