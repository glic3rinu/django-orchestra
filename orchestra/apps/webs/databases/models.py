from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators

from . import settings
from ..models import Web


class Database(models.Model):
    """ Represents a basic database for a web application """
    web = models.ForeignKey(Web, verbose_name=_("web"), related_name='databases')
    username = models.CharField(_("username"), max_length=128, unique=True,
            validators=[validators.validate_name])
    password = models.CharField(_("password"), max_length=64)
    type = models.CharField(_("type"), max_length=32,
            choices=settings.DATABASES_TYPE_CHOICES,
            default=settings.DATABASES_DEFAULT_TYPE)
    
    def __unicode__(self):
        return "%s DB" % self.web.name
