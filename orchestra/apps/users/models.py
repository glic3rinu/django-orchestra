from django.contrib.auth.hashers import make_password
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import ugettext_lazy as _


from orchestra.core import services


class User(models.Model):
    username = models.CharField(_("username"), max_length=64, unique=True,
            help_text=_("Required. 30 characters or fewer. Letters, digits and "
                        "./-/_ only."),
            validators=[validators.RegexValidator(r'^[\w.-]+$',
                        _("Enter a valid username."), 'invalid')])
    password = models.CharField(_("password"), max_length=128)
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='users')
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_active = models.BooleanField(_("active"), default=True,
            help_text=_("Designates whether this account should be treated as active. "
                        "Unselect this instead of deleting accounts."))
    
    @property
    def is_main(self):
        return self.username == self.account.username
    
    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip() or self.username
    
    def get_short_name(self):
        """ Returns the short name for the user """
        return self.first_name
    
    def get_description(self):
        return "{full_name}, {email}".format(full_name=self.get_full_name(), email=self.email)
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        """ Sends an email to this User """
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
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


services.register(User)
