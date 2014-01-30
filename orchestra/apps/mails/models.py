import os

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import settings


# TODO validations and max_length!

class MailDomain(models.Model):
    """
    Represents a domain that is associated to a mail server

    http://www.postfix.org/VIRTUAL_README.html#canonical
    """

    CANONICAL = 'CANONICAL' # Server domain name
    HOSTED = 'HOSTED'       # Other domains hosted on the server besides canonical
    RELAY = 'RELAY'         # Backup MX for other domains

    DOMAIN_TYPES = (
        (CANONICAL, _("Canonical domain")),
        (HOSTED, _("Hosted domain")),
        (RELAY, _("Relay domain")),
    )

    domain = models.OneToOneField(settings.MAILS_VIRTUAL_DOMAIN_MODEL,
            verbose_name=_("domain"))
    type = models.CharField(max_length=20, choices=DOMAIN_TYPES, default=HOSTED,
            help_text=_("Canonical: Server domain name<br>"
                        "Hosted: Other domains hosted on the server besides canonical<br>"
                        "Relay: Backup MX for other domains"))

    def __unicode__(self):
        return u"%s" % self.domain


class Mailbox(models.Model):
    """
    Represents an email box for mail delivery

    http://www.postfix.org/VIRTUAL_README.html#virtual_mailbox
    """
    user = models.OneToOneField(get_user_model(), primary_key=True,
            verbose_name=_("user"))
    emailname = models.CharField(_("email name"), max_length=23)
    domain = models.ForeignKey(MailDomain, verbose_name=_("domain"))
    home = models.CharField(_("home directory"), max_length=256, unique=True,
            blank=True)

    class Meta:
        unique_together = ('emailname', 'domain')
        verbose_name_plural = _("mailboxes")

    def __unicode__(self):
        return self.address

    def save(self, *args, **kwargs):
        """ Generates home directory, if not provided """
        if not self.home or self.home == settings.MAILS_DEFAULT_BASE_HOME:
            self.home = os.path.join(settings.MAILS_DEFAULT_BASE_HOME,
                                     self.domain.domain.name, self.emailname)
        super(Mailbox, self).save(*args, **kwargs)

    @property
    def address(self):
        return "%s@%s" % (self.emailname, self.domain)


class MailAlias(models.Model):
    """
    Represents aliases. An alias can have the following features

      * Catch-all, when emailname is not provided
      * Redirection, when destination is a full email address
      * Alias, when destination is an emailname

    http://www.postfix.org/VIRTUAL_README.html#virtual_alias
    """
    emailname = models.CharField(_("email name"), max_length=256, blank=True)
    domain = models.ForeignKey(MailDomain, verbose_name=_("domain"))
    destination = models.CharField(_("destination"), max_length=256)

    class Meta:
        unique_together = ('emailname', 'domain')
        verbose_name_plural = _("mail aliases")

    def __unicode__(self):
        return self.source

    @property
    def source(self):
        """ Parity with destination """
        return "%s@%s" % (self.emailname, self.domain)
