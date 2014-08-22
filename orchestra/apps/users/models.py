from django.contrib.auth import models as auth
from django.core import validators
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services


class User(auth.AbstractBaseUser):
    username = models.CharField(_("username"), max_length=64, unique=True,
            help_text=_("Required. 30 characters or fewer. Letters, digits and "
                        "./-/_ only."),
            validators=[validators.RegexValidator(r'^[\w.-]+$',
                        _("Enter a valid username."), 'invalid')])
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='users', null=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_superuser = models.BooleanField(_("superuser status"), default=False,
        help_text=_("Designates that this user has all permissions without "
                    "explicitly assigning them."))
    is_staff = models.BooleanField(_("staff status"), default=False,
            help_text=_("Designates whether the user can log into this admin "
                        "site."))
    is_admin = models.BooleanField(_("admin status"), default=False,
            help_text=_("Designates whether the user can administrate its account."))
    is_active = models.BooleanField(_("active"), default=True,
            help_text=_("Designates whether this user should be treated as "
                        "active. Unselect this instead of deleting accounts."))
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    
    objects = auth.UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    @property
    def is_main(self):
        return self.account.user == self
    
    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip() or self.username
    
    def get_short_name(self):
        """ Returns the short name for the user """
        return self.first_name
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        """ Sends an email to this User """
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has the specified permission. This method
        queries all available auth backends, but returns immediately if any
        backend returns True. Thus, a user who has permission from a single
        auth backend is assumed to have permission in general. If an object is
        provided, permissions for this specific object are checked.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True
        # Otherwise we need to check the backends.
        return auth._user_has_perm(self, perm, obj)
    
    def has_perms(self, perm_list, obj=None):
        """
        Returns True if the user has each of the specified permissions. If
        object is passed, it checks if the user has all required perms for this
        object.
        """
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True
    
    def has_module_perms(self, app_label):
        """
        Returns True if the user has any permissions in the given app label.
        Uses pretty much the same logic as has_perm, above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True
        return auth._user_has_module_perms(self, app_label)


services.register(User, menu=False)
