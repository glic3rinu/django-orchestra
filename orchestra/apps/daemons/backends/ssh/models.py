from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import settings


class SSHConfig(models.Model):
    """ Represents the configuration used for execting script on host via SSH """
    host = models.OneToOneField('daemons.Host', verbose_name=_("host"))
    user = models.CharField(_("user"), max_length=128,
            default=settings.DAEMONS_SSH_DEFAULT_USER,
            help_text=_("user that will execute the script on the remote host."))
    password = models.CharField(_("password"), max_length=64, blank=True,
            help_text=_("password of the remote user, but better if you use private keys."))
    host_keys = models.CharField(_("host keys"), max_length=256, blank=True,
            default=settings.DAEMONS_SSH_DEFAULT_HOST_KEYS,
            help_text=_("path of the known remote ssh host keys, "
                        "ssh fingerprinting will be skiped if not provided"))
    private_key = models.CharField("private key", max_length=256, blank=True,
            default=settings.DAEMONS_SSH_DEFAULT_PRIVATE_KEY,
            help_text=_("path of the SSH private key used for authentication"))
    port = models.IntegerField(_("port"), default=settings.DAEMONS_SSH_DEFAULT_PORT)
    
    def __unicode__(self):
        return "%s@%s" % (self.user, self.host)
