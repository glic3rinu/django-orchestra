from django.contrib.auth import models as auth
from django.conf import settings as djsettings
from django.core import validators
from django.db import models
from django.db.models.loading import get_model
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services
from orchestra.utils import send_email_template

from . import settings


class Account(auth.AbstractBaseUser):
    username = models.CharField(_("username"), max_length=64, unique=True,
            help_text=_("Required. 64 characters or fewer. Letters, digits and ./-/_ only."),
            validators=[validators.RegexValidator(r'^[\w.-]+$',
                        _("Enter a valid username."), 'invalid')])
    main_systemuser = models.ForeignKey(settings.ACCOUNTS_SYSTEMUSER_MODEL, null=True,
            related_name='accounts_main', editable=False)
    short_name = models.CharField(_("short name"), max_length=64, blank=True)
    full_name = models.CharField(_("full name"), max_length=256)
    email = models.EmailField(_('email address'), help_text=_("Used for password recovery"))
    type = models.CharField(_("type"), choices=settings.ACCOUNTS_TYPES,
            max_length=32, default=settings.ACCOUNTS_DEFAULT_TYPE)
    language = models.CharField(_("language"), max_length=2,
            choices=settings.ACCOUNTS_LANGUAGES,
            default=settings.ACCOUNTS_DEFAULT_LANGUAGE)
    comments = models.TextField(_("comments"), max_length=256, blank=True)
    is_superuser = models.BooleanField(_("superuser status"), default=False,
            help_text=_("Designates that this user has all permissions without "
                        "explicitly assigning them."))
    is_active = models.BooleanField(_("active"), default=True,
            help_text=_("Designates whether this account should be treated as active. "
                        "Unselect this instead of deleting accounts."))
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    
    objects = auth.UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __unicode__(self):
        return self.name
    
    @property
    def name(self):
        return self.username
    
    @property
    def is_staff(self):
        return self.is_superuser
    
#    @property
#    def main_systemuser(self):
#        return self.systemusers.get(is_main=True)
    
    @classmethod
    def get_main(cls):
        return cls.objects.get(pk=settings.ACCOUNTS_MAIN_PK)
    
    def save(self, active_systemuser=False, *args, **kwargs):
        created = not self.pk
        super(Account, self).save(*args, **kwargs)
        if created:
            self.main_systemuser = self.systemusers.create(account=self, username=self.username,
                    password=self.password, is_active=active_systemuser)
            self.save(update_fields=['main_systemuser'])
    
    def clean(self):
        self.short_name = self.short_name.strip()
        self.full_name = self.full_name.strip()
    
    def disable(self):
        self.is_active = False
        self.save(update_fields=['is_active'])
        # Trigger save() on related objects that depend on this account
        for rel in self._meta.get_all_related_objects():
            if not rel.model in services:
                continue
            try:
                rel.model._meta.get_field_by_name('is_active')
            except models.FieldDoesNotExist: 
                continue
            else:
                for obj in getattr(self, rel.get_accessor_name()).all():
                    obj.save(update_fields=[])
    
    def send_email(self, template, context, contacts=[], attachments=[], html=None):
        contacts = self.contacts.filter(email_usages=contacts)
        email_to = contacts.values_list('email', flat=True)
        send_email_template(template, context, email_to, html=html, attachments=attachments)
    
    def get_full_name(self):
        return self.full_name or self.short_name or self.username
    
    def get_short_name(self):
        """ Returns the short name for the user """
        return self.short_name or self.username or self.full_name
    
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
    
    def get_related_passwords(self):
        related = [
            self.main_systemuser,
        ]
        for model, key, related_kwargs, __ in settings.ACCOUNTS_CREATE_RELATED:
            if 'password' not in related_kwargs:
                continue
            model = get_model(model)
            kwargs = {
                key: eval(related_kwargs[key], {'account': self})
            }
            try:
                rel = model.objects.get(account=self, **kwargs)
            except model.DoesNotExist:
                continue
            related.append(rel)
        return related


services.register(Account, menu=False)
