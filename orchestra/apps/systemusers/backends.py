import textwrap

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.accounts.backends import MainUserBackend, MainFTPTraffic


class SystemUserBackend(MainUserBackend):
    verbose_name = _("System user")
    model = 'systemusers.SystemUser'
    ignore_fields = []


class SystemUserFTPTraffic(MainFTPTraffic):
    model = 'systemusers.SystemUser'
    verbose_name = _('System user FTP traffic')
