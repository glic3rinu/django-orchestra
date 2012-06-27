from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


MAIL_DOMAIN_TYPES = (
    ('canonical', _('Canonical domain')),
    ('hosted', _('Hosted domain')),
    ('relay', _('Relay domain')),)


class VirtualDomain(models.Model):
    """ http://www.postfix.org/VIRTUAL_README.html#canonical """
    domain = models.OneToOneField('dns.Name')
    type = models.CharField(max_length=20, choices=MAIL_DOMAIN_TYPES, default='hosted')

    def __unicode__(self):
        return str(self.domain)


class VirtualUser(models.Model):
    """ Mail users """
    user = models.OneToOneField(User, primary_key=True, unique=True)
    emailname = models.CharField(max_length=23)
    domain = models.ForeignKey(VirtualDomain)
    home = models.CharField(max_length=255, unique=True, blank=True)
    
    class Meta:
        unique_together = ("emailname", "domain")

    def __unicode__(self):
        return self.emailname

    def save(self, *args, **kwargs):
        if not self.pk and not self.home:
            self.home = "%s/%s" % (settings.DEFAULT_MAIL_HOME, self.user)
        super(VirtualUser, self).save(*args, **kwargs)

    @property
    def address(self):
        return self.emailname + '@' + str(self.domain)


class VirtualAliase(models.Model):
    """ Manages the mail server aliases (catchall, redirect, alias)"""
    emailname = models.CharField(max_length=63, blank=True)
    domain = models.ForeignKey(VirtualDomain)
    destination = models.CharField(max_length=63)

    class Meta:
        unique_together = ("emailname", "domain")

    def __unicode__(self):
        return str(self.emailname) + '@' + str(self.domain)

    @property
    def source(self):
        return self
