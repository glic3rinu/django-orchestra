from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core.validators import validate_hostname

from . import settings


class VPS(models.Model):
    hostname = models.CharField(_("hostname"), max_length=256, unique=True,
        validators=[validate_hostname])
    type = models.CharField(_("type"), max_length=64, choices=settings.VPS_TYPES,
        default=settings.VPS_DEFAULT_TYPE)
    template = models.CharField(_("template"), max_length=64,
        choices=settings.VPS_TEMPLATES, default=settings.VPS_DEFAULT_TEMPLATE)
    password = models.CharField(_('password'), max_length=128,
        help_text=_("<TT>root</TT> password of this virtual machine"))
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
        related_name='vpss')
    
    class Meta:
        verbose_name = "VPS"
        verbose_name_plural = "VPSs"
    
    def __str__(self):
        return self.hostname
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def get_username(self):
        return self.hostname
