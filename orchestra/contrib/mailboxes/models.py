import os

from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator, ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services

from . import validators, settings


class Mailbox(models.Model):
    CUSTOM = 'CUSTOM'
    
    name = models.CharField(_("name"), max_length=64, unique=True,
        help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        validators=[
            RegexValidator(r'^[\w.@+-]+$', _("Enter a valid mailbox name.")),
        ])
    password = models.CharField(_("password"), max_length=128)
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
        related_name='mailboxes')
    filtering = models.CharField(max_length=16,
        default=settings.MAILBOXES_MAILBOX_DEFAULT_FILTERING,
        choices=[(k, v[0]) for k,v in settings.MAILBOXES_MAILBOX_FILTERINGS.items()])
    custom_filtering = models.TextField(_("filtering"), blank=True,
        validators=[validators.validate_sieve],
        help_text=_("Arbitrary email filtering in sieve language. "
                    "This overrides any automatic junk email filtering"))
    is_active = models.BooleanField(_("active"), default=True)
    
    class Meta:
        verbose_name_plural = _("mailboxes")
    
    def __str__(self):
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
        return os.path.normpath(settings.MAILBOXES_HOME % context)
    
    def clean(self):
        if self.custom_filtering and self.filtering != self.CUSTOM:
            self.custom_filtering = ''
    
    def get_filtering(self):
        __, filtering = settings.MAILBOXES_MAILBOX_FILTERINGS[self.filtering]
        if isinstance(filtering, str):
            return filtering
        return filtering(self)
    
    def delete(self, *args, **kwargs):
        super(Mailbox, self).delete(*args, **kwargs)
        # Cleanup related addresses
        for address in Address.objects.filter(forward__regex=r'.*(^|\s)+%s($|\s)+.*' % self.name):
            forward = address.forward.split()
            forward.remove(self.name)
            address.forward = ' '.join(forward)
            if not address.destination:
                address.delete()
            else:
                address.save()
    
    def get_local_address(self):
        if not settings.MAILBOXES_LOCAL_ADDRESS_DOMAIN:
            raise AttributeError("Mailboxes do not have a defined local address domain.")
        return '@'.join((self.name, settings.MAILBOXES_LOCAL_ADDRESS_DOMAIN))


class Address(models.Model):
    name = models.CharField(_("name"), max_length=64, blank=True,
        validators=[validators.validate_emailname],
        help_text=_("Address name, left blank for a <i>catch-all</i> address"))
    domain = models.ForeignKey(settings.MAILBOXES_DOMAIN_MODEL,
        verbose_name=_("domain"), related_name='addresses')
    mailboxes = models.ManyToManyField(Mailbox, verbose_name=_("mailboxes"),
        related_name='addresses', blank=True)
    forward = models.CharField(_("forward"), max_length=256, blank=True,
        validators=[validators.validate_forward],
        help_text=_("Space separated email addresses or mailboxes"))
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
        related_name='addresses')
    
    class Meta:
        verbose_name_plural = _("addresses")
        unique_together = ('name', 'domain')
    
    def __str__(self):
        return self.email
    
    @property
    def email(self):
        return "%s@%s" % (self.name, self.domain)
    
    @cached_property
    def destination(self):
        destinations = list(self.mailboxes.values_list('name', flat=True))
        if self.forward:
            destinations += self.forward.split()
        return ' '.join(destinations)
    
    def clean(self):
        if self.account_id:
            forward_errors = []
            for mailbox in self.get_forward_mailboxes():
                if mailbox.account_id == self.account_id:
                    forward_errors.append(ValidationError(
                        _("Please use mailboxes field for '%s' mailbox.") % mailbox
                    ))
            if forward_errors:
                raise ValidationError({
                    'forward': forward_errors
                })
    
    def get_forward_mailboxes(self):
        for forward in self.forward.split():
            if '@' not in forward:
                try:
                    yield Mailbox.objects.get(name=forward)
                except Mailbox.DoesNotExist:
                    pass
    
    def get_mailboxes(self):
        for mailbox in self.mailboxes.all():
            yield mailbox
        for mailbox in self.get_forward_mailboxes():
            yield mailbox


class Autoresponse(models.Model):
    address = models.OneToOneField(Address, verbose_name=_("address"),
        related_name='autoresponse')
    # TODO initial_date
    subject = models.CharField(_("subject"), max_length=256)
    message = models.TextField(_("message"))
    enabled = models.BooleanField(_("enabled"), default=False)
    
    def __str__(self):
        return self.address


services.register(Mailbox)
services.register(Address)
