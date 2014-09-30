from django.conf import settings

from django.utils.translation import ugettext, ugettext_lazy as _


USERS_SHELLS = getattr(settings, 'USERS_SHELLS', (
    ('/bin/false', _("No shell, FTP only")),
    ('/bin/rsync', _("No shell, SFTP/RSYNC only")),
    ('/bin/bash', "/bin/bash"),
    ('/bin/sh', "/bin/sh"),
))

USERS_DEFAULT_SHELL = getattr(settings, 'USERS_DEFAULT_SHELL', '/bin/false')
