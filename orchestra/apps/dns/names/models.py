from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..zones.models import Zone


class Domain(models.Model):
    """ Represents any domain name (or a subdomain) that _points to_ our servers """
    name = models.CharField(_("name"), max_length=256, unique=True)
    
    def __unicode__(self):
        return self.name
    
    @property
    def zone(self):
        """ returns a related Zone if exists, None otherwise """
        tail = '.'.join(self.name.split('.')[-2:])
        for zone in Zone.objects.filter(name__endswith=tail):
            if zone.name == self.name:
                return zone
            elif zone.name.endswith(self.name):
                for record in zone.records:
                    if '%s.%s' % (record.name, zone.name) == self.name:
                        return zone
        return None
