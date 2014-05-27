from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from . import settings


class Pack(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='packs')
    name = models.CharField(_("pack"), max_length=128,
            choices=settings.PRICES_PACKS,
            default=settings.PRICES_DEFAULT_PACK)
    
    def __unicode__(self):
        return self.pack


class Price(models.Model):
    description = models.CharField(_("description"), max_length=256, unique=True)
    service = models.ForeignKey(ContentType, verbose_name=_("service"))
    expression = models.CharField(_("match"), max_length=256)
    tax = models.IntegerField(_("tax"), choices=settings.PRICES_TAXES,
            default=settings.PRICES_DEFAUL_TAX)
    active = models.BooleanField(_("is active"), default=True)
    
    def __unicode__(self):
        return self.description


class Rate(models.Model):
    price = models.ForeignKey('prices.Price', verbose_name=_("price"))
    pack = models.CharField(_("pack"), max_length=128, blank=True,
            choices=(('', _("default")),) + settings.PRICES_PACKS)
    quantity = models.PositiveIntegerField(_("quantity"), null=True, blank=True)
    value = models.DecimalField(_("price"), max_digits=12, decimal_places=2)
    
    class Meta:
        unique_together = ('price', 'pack', 'quantity')
    
    def __unicode__(self):
        return self.price
