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
        choices=settings.VPS_TEMPLATES, default=settings.VPS_DEFAULT_TEMPLATE,
        help_text=_("Initial template."))
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
        related_name='vpss')
    is_active = models.BooleanField(_("active"), default=True)
    
    class Meta:
        verbose_name = "VPS"
        verbose_name_plural = "VPSs"
    
    def __str__(self):
        return self.hostname
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def get_username(self):
        return self.hostname
    
    def disable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
    
    def enable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
    
    @property
    def active(self):
        return self.is_active and self.account.is_active

