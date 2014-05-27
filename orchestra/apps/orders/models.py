from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from . import settings


class Order(models.Model):
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='orders')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    price = models.ForeignKey(settings.ORDERS_PRICE_MODEL,
            verbose_name=_("price"), related_name='orders')
    registered_on = models.DateTimeField(_("registered on"), auto_now_add=True)
    cancelled_on = models.DateTimeField(_("cancelled on"), null=True, blank=True)
    billed_on = models.DateTimeField(_("billed on"), null=True, blank=True)
    billed_until = models.DateTimeField(_("billed until"), null=True, blank=True)
    ignore = models.BooleanField(_("ignore"), default=False)
    description = models.TextField(_("description"), blank=True)
    
    content_object = generic.GenericForeignKey()
    
    def __unicode__(self):
        return self.service


class QuotaStorage(models.Model):
    order = models.ForeignKey(Order, verbose_name=_("order"))
    value = models.BigIntegerField(_("value"))
    date = models.DateTimeField(_("date"))
    
    def __unicode__(self):
        return self.order
