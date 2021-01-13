from django.contrib.auth import models as auth
from django.conf import settings as djsettings
from django.core import validators
from django.db import models
from django.db.models import signals
from django.apps import apps
from django.utils import timezone, translation
from django.utils.translation import ugettext_lazy as _

#from orchestra.contrib.orchestration.middlewares import OperationsMiddleware
#from orchestra.contrib.orchestration import Operation
from orchestra import core
from orchestra.models.utils import has_db_field
from orchestra.utils.mail import send_email_template

from . import settings


class AccountManager(auth.UserManager):
    def get_main(self):
        return self.get(pk=settings.ACCOUNTS_MAIN_PK)


class Account(auth.AbstractBaseUser):
    # Username max_length determined by LINUX system user/group lentgh: 32
    username = models.CharField(_("username"), max_length=32, unique=True,
        help_text=_("Required. 32 characters or fewer. Letters, digits and ./-/_ only."),
        validators=[
            validators.RegexValidator(r'^[\w.-]+$', _("Enter a valid username."), 'invalid')
        ])
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
    
    objects = AccountManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return self.name
    
    @property
    def name(self):
        return self.username
    
    @property
    def is_staff(self):
        return self.is_superuser
    
    def save(self, active_systemuser=False, *args, **kwargs):
        created = not self.pk
        if not created:
            was_active = Account.objects.filter(pk=self.pk).values_list('is_active', flat=True)[0]
        super(Account, self).save(*args, **kwargs)
        if created:
            self.main_systemuser = self.systemusers.create(
                account=self, username=self.username, password=self.password,
                is_active=active_systemuser)
            self.save(update_fields=('main_systemuser',))
        elif was_active != self.is_active:
            self.notify_related()
    
    def clean(self):
        self.short_name = self.short_name.strip()
        self.full_name = self.full_name.strip()
    
    def disable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
        self.notify_related()
    
    def enable(self):
        self.is_active = True
        self.save(update_fields=('is_active',))
        self.notify_related()
    
    def get_services_to_disable(self):
        related_fields = [
            f for f in self._meta.get_fields()
            if (f.one_to_many or f.one_to_one)
            and f.auto_created and not f.concrete
        ]
        for rel in related_fields:
            source = getattr(rel, 'related_model', rel.model)
            if source in core.services and hasattr(source, 'active'):
                for obj in getattr(self, rel.get_accessor_name()).all():
                    yield obj
    
    def notify_related(self):
        """ Trigger save() on related objects that depend on this account """
        for obj in self.get_services_to_disable():
            signals.pre_save.send(sender=type(obj), instance=obj)
            signals.post_save.send(sender=type(obj), instance=obj)
#            OperationsMiddleware.collect(Operation.SAVE, instance=obj, update_fields=())
    
    def get_contacts_emails(self, usages=None):
        contacts = self.contacts.all()
        if usages is not None:
            contactes = contacts.filter(email_usages=usages)
        return contacts.values_list('email', flat=True)
    
    def send_email(self, template, context, email_from=None, usages=None, attachments=[], html=None):
        contacts = self.contacts.filter(email_usages=usages)
        email_to = self.get_contacts_emails(usages)
        extra_context = {
            'account': self,
            'email_from': email_from or djsettings.SERVER_EMAIL,
        }
        extra_context.update(context)
        with translation.override(self.language):
            send_email_template(template, extra_context, email_to, email_from=email_from,
                html=html, attachments=attachments)
    
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
        applabel.action_modelname
        """
        if not self.is_active:
            return False
        # Active superusers have all permissions.
        if self.is_superuser:
            return True
        app, action_model = perm.split('.')
        action, model = action_model.split('_', 1)
        service_apps = set(model._meta.app_label for model in core.services.get().keys())
        accounting_apps = set(model._meta.app_label for model in core.accounts.get().keys())
        import inspect
        if ((app in service_apps or (action == 'view' and app in accounting_apps))):
            # class-level permissions
            if inspect.isclass(obj):
                return True
            elif obj and getattr(obj, 'account', None) == self:
                return True

    
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

    def get_related_passwords(self, db_field=False):
        related = [
            self.main_systemuser,
        ]
        for model, key, related_kwargs, __ in settings.ACCOUNTS_CREATE_RELATED:
            if 'password' not in related_kwargs:
                continue
            model = apps.get_model(model)
            kwargs = {
                key: eval(related_kwargs[key], {'account': self})
            }
            try:
                rel = model.objects.get(account=self, **kwargs)
            except model.DoesNotExist:
                continue
            if db_field:
                if not has_db_field(rel, 'password'):
                    continue
            related.append(rel)
        return related
