import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators

from ..models import Web


class WebFTPAccount(models.Model):
    """ Represents an FTP account for accessing a related web application """
    web = models.ForeignKey(Web, verbose_name=_("web"), related_name='webftpaccounts')
    username = models.CharField(_("username"), max_length=128, unique=True,
            validators=[validators.validate_name])
    password = models.CharField(_("password"), max_length=64)
    directory = models.CharField(_("directory"), max_length=256, blank=True,
            help_text=_("Subdirectory in relation to app directory"),)
    
    def __unicode__(self):
        return "%s@%s" % (self.username, self.web.name)
    
    @property
    def home(self):
        return os.path.join(self.web.root, self.directory)
