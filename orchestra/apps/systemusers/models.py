from django.contrib.auth.hashers import make_password
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services

from . import settings


class SystemUserQuerySet(models.QuerySet):
    def create_user(self, username, password='', **kwargs):
        user = super(SystemUserQuerySet, self).create(username=username, **kwargs)
        user.set_password(password)
        user.save(update_fields=['password'])


class SystemUser(models.Model):
    """ System users """
    username = models.CharField(_("username"), max_length=64, unique=True,
            help_text=_("Required. 30 characters or fewer. Letters, digits and ./-/_ only."),
            validators=[validators.RegexValidator(r'^[\w.-]+$',
                        _("Enter a valid username."), 'invalid')])
    password = models.CharField(_("password"), max_length=128)
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='systemusers')
    home = models.CharField(_("home"), max_length=256, blank=True,
            help_text=_("Home directory relative to account's ~main_user"))
    shell = models.CharField(_("shell"), max_length=32,
            choices=settings.USERS_SHELLS, default=settings.USERS_DEFAULT_SHELL)
    groups = models.ManyToManyField('systemusers.Group', blank=True,
            help_text=_("A new group will be created for the user. "
                        "Which additional groups would you like them to be a member of?"))
    is_main = models.BooleanField(_("is main"), default=False)
    is_active = models.BooleanField(_("active"), default=True,
            help_text=_("Designates whether this account should be treated as active. "
                        "Unselect this instead of deleting accounts."))
    
    objects = SystemUserQuerySet.as_manager()
    
    def __unicode__(self):
        return self.username
    
    def clean(self):
        """ unique usernames between accounts and system users """
        if not self.pk:
            field = self._meta.get_field_by_name('account')[0]
            account_model = field.rel.to
            if account_model.objects.filter(username=self.username).exists():
                raise validators.ValidationError(self.error_messages['duplicate_username'])
    
    def save(self, *args, **kwargs):
        created = not self.pk
        super(SystemUser, self).save(*args, **kwargs)
        if created:
            self.groups.get_or_create(name=self.username, account=self.account)
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def get_is_active(self):
        return self.account.is_active and self.is_active


class Group(models.Model):
    name = models.CharField(_("name"), max_length=64, unique=True,
            help_text=_("Required. 30 characters or fewer. Letters, digits and ./-/_ only."),
            validators=[validators.RegexValidator(r'^[\w.-]+$',
                        _("Enter a valid group name."), 'invalid')])
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='groups')
    
    def __unicode__(self):
        return self.name


services.register(SystemUser)
