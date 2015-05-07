import os

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators

from . import settings


class SystemUserQuerySet(models.QuerySet):
    def create_user(self, username, password='', **kwargs):
        user = super(SystemUserQuerySet, self).create(username=username, **kwargs)
        user.set_password(password)
        user.save(update_fields=['password'])
        return user


class SystemUser(models.Model):
    """
    System users
    
    Username max_length determined by LINUX system user lentgh: 32
    """
    username = models.CharField(_("username"), max_length=32, unique=True,
        help_text=_("Required. 64 characters or fewer. Letters, digits and ./-/_ only."),
        validators=[validators.validate_username])
    password = models.CharField(_("password"), max_length=128)
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
        related_name='systemusers')
    home = models.CharField(_("home"), max_length=256, blank=True,
        help_text=_("Starting location when login with this no-shell user."))
    directory = models.CharField(_("directory"), max_length=256, blank=True,
        help_text=_("Optional directory relative to user's home."))
    shell = models.CharField(_("shell"), max_length=32, choices=settings.SYSTEMUSERS_SHELLS,
        default=settings.SYSTEMUSERS_DEFAULT_SHELL)
    groups = models.ManyToManyField('self', blank=True,  symmetrical=False,
        help_text=_("A new group will be created for the user. "
                    "Which additional groups would you like them to be a member of?"))
    is_active = models.BooleanField(_("active"), default=True,
        help_text=_("Designates whether this account should be treated as active. "
                    "Unselect this instead of deleting accounts."))
    
    objects = SystemUserQuerySet.as_manager()
    
    def __str__(self):
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
    
    @property
    def has_shell(self):
        return self.shell not in settings.SYSTEMUSERS_DISABLED_SHELLS
    
    def get_description(self):
        return self.get_shell_display()
    
    def save(self, *args, **kwargs):
        if not self.home:
            self.home = self.get_base_home()
        super(SystemUser, self).save(*args, **kwargs)
    
    def clean(self):
        if self.home:
            self.home = os.path.normpath(self.home)
        if self.directory:
            directory_error = None
            if self.has_shell:
                directory_error = _("Directory with shell users can not be specified.")
            elif self.account_id and self.is_main:
                directory_error = _("Directory with main system users can not be specified.")
            elif self.home == self.get_base_home():
                directory_error = _("Directory on the user's base home is not allowed.")
            if directory_error:
                raise ValidationError({
                    'directory': directory_error,
                })
        if self.has_shell and self.home and self.home != self.get_base_home():
            raise ValidationError({
                'home': _("Shell users should use their own home."),
            })
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def get_base_home(self):
        context = {
            'user': self.username,
            'username': self.username,
        }
        return os.path.normpath(settings.SYSTEMUSERS_HOME % context)
    
    def get_home(self):
        return os.path.normpath(os.path.join(self.home, self.directory))
