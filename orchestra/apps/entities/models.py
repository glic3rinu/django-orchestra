from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import settings


class Entity(models.Model):
    """ 
    Represents a customer or member, depending on the context,
    with contact information and related contracted services
    """
    short_name = models.CharField(_("short name"), max_length=128)
    full_name = models.CharField(_("full name"), max_length=256, blank=True,
            unique=True)
    national_id = models.CharField(_("national ID"), max_length=64)
    address = models.CharField(_("address"), max_length=256, blank=True)
    city = models.CharField(_("city"), max_length=128, blank=True,
            default=settings.ENTITIES_DEFAULT_CITY)
    zipcode = models.PositiveIntegerField(_("zip code"), blank=True, null=True)
    province = models.CharField(_("province"), max_length=20, blank=True,
            default=settings.ENTITIES_DEFAULT_PROVINCE)
    country = models.CharField(_("country"), max_length=20,
            default=settings.ENTITIES_DEFAULT_COUNTRY)
    type = models.CharField(_("type"), max_length=32,
            choices=settings.ENTITIES_TYPE_CHOICES,
            default=settings.ENTITIES_DEFAULT_TYPE)
    comments = models.TextField(_("comments"), max_length=256, blank=True)
    language = models.CharField(_("language"), max_length=2,
            choices=settings.ENTITIES_LANGUAGE_CHOICES,
            default=settings.ENTITIES_DEFAULT_LANGUAGE)
    register_date = models.DateTimeField(_("register date"), auto_now_add=True)
    
    class Meta:
        verbose_name_plural = _("entities")
    
    def __unicode__(self):
        return self.full_name


class Contract(models.Model):
    """ Represents contracted services by a particular entity """
    entity = models.ForeignKey(_("entity"), Entity)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(null=True)
    service = generic.GenericForeignKey()
    description = models.CharField(_("description"), max_length=256, blank=True)
    register_date = models.DateTimeField(_("eegister date"), auto_now_add=True)
    cancel_date = models.DateTimeField(_("cancel date"), null=True, blank=True)
    
    class Meta:
        unique_together = ('content_type', 'object_id')
    
    def __unicode__(self):
        return "<%s: %s>" % (self.entity, str(self.service))
    
    def cancel(self):
        self.cancel_date=datetime.now()
        self.save()
    
    @property
    def is_canceled(self):
        if self.cancel_date and self.cancel_date < datetime.now():
            return True
        return False
