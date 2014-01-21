from django.db import models
from django.utils.translation import ugettext_lazy as _


class Name(models.Model):
    """ Represents any domain name (or a subdomain) that _points to_ our servers """
    name = models.CharField(_("name"), max_length=256, unique=True)
    
    def __unicode__(self):
        return self.name
