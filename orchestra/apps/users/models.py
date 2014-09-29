from django.contrib.auth.hashers import make_password
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services

from . import settings


class User(models.Model):
    """ System users """
    username = models.CharField(_("username"), max_length=64, unique=True,
            help_text=_("Required. 30 characters or fewer. Letters, digits and ./-/_ only."),
            validators=[validators.RegexValidator(r'^[\w.-]+$',
                        _("Enter a valid username."), 'invalid')])
    password = models.CharField(_("password"), max_length=128)
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='users')
    home = models.CharField(_("home"), max_length=256, blank=True,
            help_text=_("Home directory relative to account's ~primary_user"))
    shell = models.CharField(_("shell"), max_length=32,
            choices=settings.USERS_SHELLS, default=settings.USERS_DEFAULT_SHELL)
    groups = models.ManyToManyField('users.User', blank=True,
            help_text=_("A new group will be created for the user. "
                        "Which additional groups would you like them to be a member of?"))
    is_active = models.BooleanField(_("active"), default=True,
            help_text=_("Designates whether this account should be treated as active. "
                        "Unselect this instead of deleting accounts."))
    
    def __unicode__(self):
        return self.username
    
    @property
    def is_main(self):
        return self.username == self.account.username
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])
    
    def get_is_active(self):
        return self.account.is_active and self.is_active


services.register(User)
