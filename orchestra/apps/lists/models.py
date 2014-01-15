from django.db import models
from django.utils.translation import ugettext_lazy as _


class List(models.Model):
    name = models.CharField(_("name"), max_length=128)
    domain = models.ForeignKey(settings.LISTS_DOMAIN_MODEL, verbose_name=_("domain"))
    admin = models.EmailField(_("admin"), help_text=_("administration email address"))
    password = models.CharField(_("password"), max_length=128)
    
    class Meta:
        unique_together = ('name', 'domain')
    
    def __unicode__(self):
        return "%s@%s" % (self.name, self.domain)

