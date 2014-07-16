from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services

from . import settings


class Pack(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='packs')
    name = models.CharField(_("pack"), max_length=128,
            choices=settings.PRICES_PACKS,
            default=settings.PRICES_DEFAULT_PACK)
    
    def __unicode__(self):
        return self.pack


class Rate(models.Model):
    service = models.ForeignKey('orders.Service', verbose_name=_("service"))
    pack = models.CharField(_("pack"), max_length=128, blank=True,
            choices=(('', _("default")),) + settings.PRICES_PACKS)
    quantity = models.PositiveIntegerField(_("quantity"), null=True, blank=True)
    value = models.DecimalField(_("value"), max_digits=12, decimal_places=2)
    
    class Meta:
        unique_together = ('service', 'pack', 'quantity')
    
    def __unicode__(self):
        return "{}-{}".format(str(self.value), self.quantity)


services.register(Pack, menu=False)
