from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext as _

from . import settings


class Service(models.Model):
    name = models.CharField(_("name"), max_length=256)
    content_type = models.ForeignKey(ContentType, verbose_name=_("content_type"))
    match = models.CharField(_("expression"), max_length=256)
    
    def __unicode__(self):
        return self.name


class Order(models.Model):
    contact = models.ForeignKey(settings.ORDERS_CONTACT_MODEL,
            verbose_name=_("contact"), related_name='orders')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    service = models.ForeignKey(Service, verbose_name=_("service"),
            related_name='orders'))
    registered_on = models.DateTimeField(_("registered on"), auto_now_add=True)
    canceled_on = models.DateTimeField(_("canceled on"), null=True, blank=True)
    last_billed_on = models.DateTimeField(_("last billed on"), null=True, blank=True)
    billed_until = models.DateTimeField(_("billed until"), null=True, blank=True)
    ignore = models.BooleanField(_("ignore"), default=False)
    description = models.CharField(_("description"), max_length=256, blank=True)
    
    content_object = generic.GenericForeignKey()
    
    def __unicode__(self):
        return "%s@%s" (self.service, self.contact)

