from django.conf import settings

from django.utils.translation import ugettext, ugettext_lazy as _


SYSTEMUSERS_SHELLS = getattr(settings, 'SYSTEMUSERS_SHELLS', (
    ('/bin/false', _("No shell, FTP only")),
    ('/bin/rsync', _("No shell, SFTP/RSYNC only")),
    ('/bin/bash', "/bin/bash"),
    ('/bin/sh', "/bin/sh"),
))

SYSTEMUSERS_DEFAULT_SHELL = getattr(settings, 'SYSTEMUSERS_DEFAULT_SHELL', '/bin/false')


SYSTEMUSERS_HOME = getattr(settings, 'SYSTEMUSERS_HOME', '/home/%(username)s')


SYSTEMUSERS_FTP_LOG_PATH = getattr(settings, 'SYSTEMUSERS_FTP_LOG_PATH', '/var/log/vsftpd.log')
