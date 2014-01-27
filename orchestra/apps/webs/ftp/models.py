from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators

from ..models import Web


class FTP(models.Model):
    """ Represents an FTP account for accessing a related web application """
    web = models.ForeignKey(Web, verbose_name=_("web"))
    username = models.CharField(_("username"), max_length=128, unique=True,
            validators=[validators.validate_name])
    password = models.CharField(_("password"), max_length=64)
    
    def __unicode__(self):
        return "%s@%s" % (self.username, self.web.name)
