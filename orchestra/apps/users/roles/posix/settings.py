from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _


POSIX_SHELLS = getattr(settings, 'POSIX_SHELLS', (
    ('/bin/false', _("FTP/sFTP only")),
    ('/bin/rsync', _("rsync shell")),
    ('/bin/bash', "Bash"),
))

POSIX_DEFAULT_SHELL = getattr(settings, 'POSIX_DEFAULT_SHELL', '/bin/false')
