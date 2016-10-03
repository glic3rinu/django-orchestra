import os
import re
from collections import defaultdict

from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator, ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from . import validators, settings


class Mailbox(models.Model):
    CUSTOM = 'CUSTOM'
    
    name = models.CharField(_("name"), unique=True, db_index=True,
        max_length=settings.MAILBOXES_NAME_MAX_LENGTH,
        help_text=_("Required. %s characters or fewer. Letters, digits and ./-/_ only.") %
            settings.MAILBOXES_NAME_MAX_LENGTH,
        validators=[
            RegexValidator(r'^[\w.-]+$', _("Enter a valid mailbox name.")),
        ])
    password = models.CharField(_("password"), max_length=128)
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
        related_name='mailboxes')
    filtering = models.CharField(max_length=16,
        default=settings.MAILBOXES_MAILBOX_DEFAULT_FILTERING,
        choices=[(k, v[0]) for k,v in sorted(settings.MAILBOXES_MAILBOX_FILTERINGS.items())])
    custom_filtering = models.TextField(_("filtering"), blank=True,
        validators=[validators.validate_sieve],
        help_text=_("Arbitrary email filtering in "
                    "<a href='https://tty1.net/blog/2011/sieve-tutorial_en.html'>sieve language</a>. "
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
    
    def disable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
    
    def enable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def get_home(self):
        context = {
            'name': self.name,
            'username': self.name,
        }
        return os.path.normpath(settings.MAILBOXES_HOME % context)
    
    def clean(self):
        if self.filtering == self.CUSTOM and not self.custom_filtering:
            raise ValidationError({
                'custom_filtering': _("Custom filtering is selected but not provided.")
            })
    
    def get_filtering(self):
        name, content = settings.MAILBOXES_MAILBOX_FILTERINGS[self.filtering]
        if callable(content):
            # Custom filtering
            content = content(self)
        return (name, content)
    
    def get_local_address(self):
        if not settings.MAILBOXES_LOCAL_DOMAIN:
            raise AttributeError("Mailboxes do not have a defined local address domain.")
        return '@'.join((self.name, settings.MAILBOXES_LOCAL_DOMAIN))
    
    def get_forwards(self):
        return Address.objects.filter(forward__regex=r'(^|.*\s)%s(\s.*|$)' % self.name)
    
    def get_addresses(self):
        mboxes = self.addresses.all()
        forwards = self.get_forwards()
        return set(mboxes).union(set(forwards))


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
        errors = defaultdict(list)
        local_domain = settings.MAILBOXES_LOCAL_DOMAIN
        if local_domain:
            forwards = self.forward.split()
            for ix, forward in enumerate(forwards):
                if forward.endswith('@%s' % local_domain):
                    name = forward.split('@')[0]
                    if Mailbox.objects.filter(name=name).exists():
                        forwards[ix] = name
            self.forward = ' '.join(forwards)
        if self.account_id:
            for mailbox in self.get_forward_mailboxes():
                if mailbox.account_id == self.account_id:
                    errors['forward'].append(
                        _("Please use mailboxes field for '%s' mailbox.") % mailbox
                    )
        if self.domain:
            for forward in self.forward.split():
                if self.email == forward:
                    errors['forward'].append(
                        _("'%s' forwards to itself.") % forward
                    )
        if errors:
            raise ValidationError(errors)
    
    def get_forward_mailboxes(self):
        rm_local_domain = re.compile(r'@%s$' % settings.MAILBOXES_LOCAL_DOMAIN)
        mailboxes = []
        for forward in self.forward.split():
            forward = rm_local_domain.sub('', forward)
            if '@' not in forward:
                mailboxes.append(forward)
        return Mailbox.objects.filter(name__in=mailboxes)
    
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
