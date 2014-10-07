from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services

from . import validators, settings

# TODO rename app to mailboxes

class Mailbox(models.Model):
    name = models.CharField(_("name"), max_length=64, unique=True,
            help_text=_("Required. 30 characters or fewer. Letters, digits and "
                        "@/./+/-/_ only."),
            validators=[RegexValidator(r'^[\w.@+-]+$',
                        _("Enter a valid mailbox name."), 'invalid')])
    password = models.CharField(_("password"), max_length=128)
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='mailboxes')
    custom_filtering = models.TextField(_("filtering"), blank=True,
            validators=[validators.validate_sieve],
            help_text=_("Arbitrary email filtering in sieve language. "
                        "This overrides any automatic junk email filtering"))
    is_active = models.BooleanField(_("active"), default=True)
#    addresses = models.ManyToManyField('mails.Address',
#            verbose_name=_("addresses"),
#            related_name='mailboxes', blank=True)
    
    class Meta:
        verbose_name_plural = _("mailboxes")
    
    def __unicode__(self):
        return self.name
    
    @cached_property
    def active(self):
        try:
            return self.is_active and self.account.is_active
        except type(self).account.field.rel.to.DoesNotExist:
            return self.is_active
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def get_home(self):
        context = {
            'name': self.name,
            'username': self.name,
        }
        home = settings.MAILS_HOME % context
        return home.rstrip('/')


class Address(models.Model):
    name = models.CharField(_("name"), max_length=64,
            validators=[validators.validate_emailname])
    domain = models.ForeignKey(settings.MAILS_DOMAIN_MODEL,
            verbose_name=_("domain"),
            related_name='addresses')
    mailboxes = models.ManyToManyField(Mailbox,
            verbose_name=_("mailboxes"),
            related_name='addresses', blank=True)
    forward = models.CharField(_("forward"), max_length=256, blank=True,
            validators=[validators.validate_forward], help_text=_("Space separated email addresses"))
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='addresses')
    
    class Meta:
        verbose_name_plural = _("addresses")
        unique_together = ('name', 'domain')
    
    def __unicode__(self):
        return self.email
    
    @property
    def email(self):
        return "%s@%s" % (self.name, self.domain)
    
    @property
    def destination(self):
        destinations = list(self.mailboxes.values_list('name', flat=True))
        if self.forward:
            destinations.append(self.forward)
        return ' '.join(destinations)


class Autoresponse(models.Model):
    address = models.OneToOneField(Address, verbose_name=_("address"),
            related_name='autoresponse')
    # TODO initial_date
    subject = models.CharField(_("subject"), max_length=256)
    message = models.TextField(_("message"))
    enabled = models.BooleanField(_("enabled"), default=False)
    
    def __unicode__(self):
        return self.address


services.register(Mailbox)
services.register(Address)
