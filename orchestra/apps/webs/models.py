from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators

from . import settings


# TODO validators
class Web(models.Model):
    """ Represents a web application """
    user = models.ForeignKey(get_user_model(), verbose_name=_("user"), related_name='webs')
    name = models.CharField(_("name"), max_length=128, unique=True,
            validators=[validators.validate_name])
    port = models.PositiveIntegerField(_("port"), choices=settings.WEBS_PORT_CHOICES,
            default=settings.WEBS_DEFAULT_PORT)
    domains = models.ManyToManyField(settings.WEBS_DOMAIN_MODEL, verbose_name=_("domains"))
    root = models.CharField(_("root"), max_length=256, blank=True,
            default=settings.WEBS_DEFAULT_ROOT)
    type = models.CharField(_("type"), max_length=32,
            choices=settings.WEBS_TYPE_CHOICES,
            default=settings.WEBS_DEFAULT_TYPE)
    directives = models.TextField(blank=True)
    is_active = models.BooleanField(_("is active"), default=True)
    
    def __unicode__(self):
        return self.name
