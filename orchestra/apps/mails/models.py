import re

from django.contrib.auth.hashers import check_password, make_password
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services

from . import validators, settings


class Mailbox(models.Model):
    name = models.CharField(_("name"), max_length=64, unique=True,
            help_text=_("Required. 30 characters or fewer. Letters, digits and "
                        "@/./+/-/_ only."),
            validators=[RegexValidator(r'^[\w.@+-]+$',
                        _("Enter a valid username."), 'invalid')])
    use_custom_filtering = models.BooleanField(_("Use custom filtering"),
            default=False)
    custom_filtering = models.TextField(_("filtering"), blank=True,
            validators=[validators.validate_sieve],
            help_text=_("Arbitrary email filtering in sieve language."))
    
    class Meta:
        verbose_name_plural = _("mailboxes")
    
    def __unicode__(self):
        return self.user.username
    
#    def get_addresses(self):
#        regex = r'(^|\s)+%s(\s|$)+' % self.user.username
#        return Address.objects.filter(destination__regex=regex)
#    
#    def delete(self, *args, **kwargs):
#        """ Update related addresses """
#        regex = re.compile(r'(^|\s)+(\s*%s)(\s|$)+' % self.user.username)
#        super(Mailbox, self).delete(*args, **kwargs)
#        for address in self.get_addresses():
#            address.destination = regex.sub(r'\3', address.destination).strip()
#            if not address.destination:
#                address.delete()
#            else:
#                address.save()


#class Address(models.Model):
#    name = models.CharField(_("name"), max_length=64,
#            validators=[validators.validate_emailname])
#    domain = models.ForeignKey(settings.EMAILS_DOMAIN_MODEL,
#            verbose_name=_("domain"),
#            related_name='addresses')
#    destination = models.CharField(_("destination"), max_length=256,
#            validators=[validators.validate_destination],
#            help_text=_("Space separated mailbox names or email addresses"))
#    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
#            related_name='addresses')
#    
#    class Meta:
#        verbose_name_plural = _("addresses")
#        unique_together = ('name', 'domain')
#    
#    def __unicode__(self):
#        return self.email
#    
#    @property
#    def email(self):
#        return "%s@%s" % (self.name, self.domain)
#    
#    def get_mailboxes(self):
#        for dest in self.destination.split():
#            if '@' not in dest:
#                yield Mailbox.objects.select_related('user').get(user__username=dest)


class Address(models.Model):
    name = models.CharField(_("name"), max_length=64,
            validators=[validators.validate_emailname])
    domain = models.ForeignKey(settings.EMAILS_DOMAIN_MODEL,
            verbose_name=_("domain"),
            related_name='addresses')
    mailboxes = models.ManyToManyField('mail.Mailbox', verbose_name=_("mailboxes"),
            related_name='addresses', blank=True)
    forward = models.CharField(_("forward"), max_length=256, blank=True,
            validators=[validators.validate_forward])
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


class Autoresponse(models.Model):
    address = models.OneToOneField(Address, verbose_name=_("address"),
            related_name='autoresponse')
    # TODO initial_date
    subject = models.CharField(_("subject"), max_length=256)
    message = models.TextField(_("message"))
    enabled = models.BooleanField(_("enabled"), default=False)
    
    def __unicode__(self):
        return self.address


services.register(Address)
