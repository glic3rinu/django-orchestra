import os

from django.contrib.auth.hashers import make_password
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services

from . import settings


class SystemUserQuerySet(models.QuerySet):
    def create_user(self, username, password='', **kwargs):
        user = super(SystemUserQuerySet, self).create(username=username, **kwargs)
        user.set_password(password)
        user.save(update_fields=['password'])
        return user


class SystemUser(models.Model):
    """ System users """
    username = models.CharField(_("username"), max_length=64, unique=True,
            help_text=_("Required. 64 characters or fewer. Letters, digits and ./-/_ only."),
            validators=[validators.RegexValidator(r'^[\w.-]+$',
                        _("Enter a valid username."), 'invalid')])
    password = models.CharField(_("password"), max_length=128)
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='systemusers')
    home = models.CharField(_("home"), max_length=256, blank=True,
            help_text=_("Home directory relative to account's ~main_user"))
    shell = models.CharField(_("shell"), max_length=32,
            choices=settings.SYSTEMUSERS_SHELLS, default=settings.SYSTEMUSERS_DEFAULT_SHELL)
    groups = models.ManyToManyField('self', blank=True,  symmetrical=False,
            help_text=_("A new group will be created for the user. "
                        "Which additional groups would you like them to be a member of?"))
#    is_main = models.BooleanField(_("is main"), default=False)
    is_active = models.BooleanField(_("active"), default=True,
            help_text=_("Designates whether this account should be treated as active. "
                        "Unselect this instead of deleting accounts."))
    
    objects = SystemUserQuerySet.as_manager()
    
    def __unicode__(self):
        return self.username
    
    @cached_property
    def active(self):
        try:
            return self.is_active and self.account.is_active
        except type(self).account.field.rel.to.DoesNotExist:
            return self.is_active
    
    @cached_property
    def is_main(self):
        # TODO on account delete
        # On account creation main_systemuser_id is still None
        if self.account.main_systemuser_id:
            return self.account.main_systemuser_id == self.pk
        return self.account.username == self.username
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def get_home(self):
        if self.is_main:
            context = {
                'username': self.username,
            }
            basehome = settings.SYSTEMUSERS_HOME % context
        else:
            basehome = self.account.main_systemuser.get_home()
        return os.path.join(basehome, self.home)


services.register(SystemUser)
