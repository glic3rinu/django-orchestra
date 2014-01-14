import os

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import settings


# TODO validations and max_length!

class VirtualDomain(models.Model):
    """
    Represents a virtual domain, used for mail servers
    
    http://www.postfix.org/VIRTUAL_README.html#canonical
    """
    
    CANONICAL = 'canonical' # Server domain name
    HOSTED = 'hosted'       # Other domains hosted on the server besides canonical
    RELAY = 'relay'         # Backup MX for other domains
    
    DOMAIN_TYPES = (
        (CANONICAL, _('Canonical domain')),
        (HOSTED, _('Hosted domain')),
        (RELAY, _('Relay domain')),
    )
    
    domain = models.OneToOneField(settings.EMAILS_VIRTUAL_DOMAIN_MODEL,
            verbose_name=_("Domain"))
    type = models.CharField(max_length=20, choices=DOMAIN_TYPES, default=HOSTED)
    
    def __unicode__(self):
        return str(self.domain)


class VirtualUser(models.Model):
    """
    Represents a virtual mail box 
    
    http://www.postfix.org/VIRTUAL_README.html#virtual_mailbox
    """
    user = models.OneToOneField(User, primary_key=True, verbose_name=_("User"))
    emailname = models.CharField(_("Email name"), max_length=23)
    domain = models.ForeignKey(VirtualDomain, verbose_name=_("Domain"))
    home = models.CharField(_("Home directory"), max_length=256, unique=True,
            blank=True, default=settings.EMAILS_DEFAULT_BASE_HOME)
    
    class Meta:
        unique_together = ("emailname", "domain")
    
    def __unicode__(self):
        return self.address
    
    def save(self, *args, **kwargs):
        """ Generates home directory, if not provided """
        if not self.pk and (not self.home or self.home == settings.EMAILS_DEFAULT_BASE_HOME):
            self.home = os.path.join(settings.EMAILS_DEFAULT_BASE_HOME, self.user)
        super(VirtualUser, self).save(*args, **kwargs)
    
    @property
    def address(self):
        return "%s@%s" % (self.emailname, self.domain)


class VirtualAliase(models.Model):
    """
    Represents virtual alias
    
      * Catch-all, when emailname is not provided
      * Redirection, when destination is a full email address
      * Alias, when destination is an emailname
    
    http://www.postfix.org/VIRTUAL_README.html#virtual_alias
    """
    emailname = models.CharField(_("Email name"), max_length=256, blank=True)
    domain = models.ForeignKey(VirtualDomain, verbose_name=_("Domain"))
    destination = models.CharField(_("Destination"), max_length=256)
    
    class Meta:
        unique_together = ("emailname", "domain")
    
    def __unicode__(self):
        return self.source
    
    @property
    def source(self):
        """ Parity with destination """
        return "%s@%s" % (self.emailname, self.domain)
