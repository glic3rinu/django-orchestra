from django.db import models
from django.utils.translation import ugettext_lazy as _

from .. import roles

from . import settings


class POSIX(models.Model):
    user = models.OneToOneField('users.User', verbose_name=_("user"),
            related_name='posix')
    home = models.CharField(_("home"), max_length=256, blank=True,
            help_text=_("Home directory relative to account's ~primary_user"))
    shell = models.CharField(_("shell"), max_length=32,
            choices=settings.POSIX_SHELLS, default=settings.POSIX_DEFAULT_SHELL)
    
    def __unicode__(self):
        return str(self.user)


roles.register('posix', POSIX)
