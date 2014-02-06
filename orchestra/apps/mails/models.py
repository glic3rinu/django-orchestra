import base64
import hashlib
import os
import random
import string

from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.db import models
from django.db.models.loading import get_model
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
    SALT_LEN = 96

    user = models.OneToOneField(get_user_model(), primary_key=True,
            verbose_name=_("user"))
    emailname = models.CharField(_("email name"), max_length=23)
    domain = models.ForeignKey(MailDomain, verbose_name=_("domain"))
    home = models.CharField(_("home directory"), max_length=256, unique=True,
            blank=True)

    salt = models.CharField(max_length=SALT_LEN, blank=True,
                            help_text='Random password salt.')
    shadigest = models.CharField(max_length=256, blank=True,
                                 help_text='Base64 encoding of SHA1 digest:'
                                           'Base64(sha1(password + salt) + salt).')

    def _get_digest(self, raw_password, salt):
        """
        Returns a base64 encoded SHA1 digest using the provided
        raw_password and salt.  The digest is encoded using the
        following format:

        Base64(sha1(raw_password + salt) + salt)
        """
        # base64 does not work on unicode, so convert all django unicode strings
        # into normalized strings firt. Use str, since it will throw an error
        # if there are non-ascii characters
        m = hashlib.sha1()
        m.update(str(raw_password))
        m.update(str(salt))
        digest = base64.b64encode(m.digest() + str(self.salt))
        return digest

    def set_password(self, raw_password):
        """
        Sets the mail user password.  The Password is a base64 encoding
        of the SHA1 digest with the salt appended.  The SHA1 digest is
        the SHA1 of the raw password with the salt appended.  This is a
        compatible method of authentication with mail services such as
        dovecot.

        Ex: shadigest = Base64(sha1(password + salt) + salt)
        """
        # new salt, avoid whitespace
        chars = string.letters + string.digits + string.punctuation
        self.salt = ''.join(random.choice(chars) for x in xrange(self.SALT_LEN))
        self.shadigest = self._get_digest(raw_password, self.salt)

    def check_password(self, raw_password):
        """
        Returns True if the given raw string is the correct password
        for the mail user. (This takes care of the password hashing in
        making the comparison.)
        """
        digest = self._get_digest(raw_password, self.salt)
        if self.shadigest == digest:
            return True
        else:
            return False

    @classmethod
    def get_from_email(cls, email):
        """
        Return a valid `Mailbox` instance from an email address.  If
        the domain does not exist, `Domain.DoesNotExist` is raised.  If
        the user does not exist, but the domain does exist, then
        `Mailbox.DoesNotExist` is raised. If the email is not parseable
        then a `ValidationError` is raised.
        """
        email = email.strip().lower()
        validate_email(email)

        emailname, name = email.split('@')
        emailname = emailname.strip()

        domain = MailDomain.objects.get(domain__name=name)
        user = Mailbox.objects.get(emailname=emailname, domain=domain)
        return user

    class Meta:
        unique_together = ('emailname', 'domain')
        verbose_name_plural = _("mailboxes")

    def __unicode__(self):
        return self.address

    def save(self, *args, **kwargs):
        """ Generates home directory, if not provided """
        self.emailname = self.emailname.lower()
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
