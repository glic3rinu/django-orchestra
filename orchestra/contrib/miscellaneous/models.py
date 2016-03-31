from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core.validators import validate_name
from orchestra.models.fields import NullableCharField


class MiscService(models.Model):
    name = models.CharField(_("name"), max_length=32, unique=True, validators=[validate_name],
        help_text=_("Raw name used for internal referenciation, i.e. service match definition"))
    verbose_name = models.CharField(_("verbose name"), max_length=256, blank=True,
        help_text=_("Human readable name"))
    description = models.TextField(_("description"), blank=True,
        help_text=_("Optional description"))
    has_identifier = models.BooleanField(_("has identifier"), default=True,
        help_text=_("Designates if this service has a <b>unique text</b> field that "
                    "identifies it or not."))
    has_amount = models.BooleanField(_("has amount"), default=False,
        help_text=_("Designates whether this service has <tt>amount</tt> "
                    "property or not."))
    is_active = models.BooleanField(_("active"), default=True,
        help_text=_("Whether new instances of this service can be created "
                    "or not. Unselect this instead of deleting services."))
    
    def __str__(self):
        return self.name
    
    def clean(self):
        self.verbose_name = self.verbose_name.strip()
    
    def get_verbose_name(self):
        return self.verbose_name or self.name
    
    def disable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
    
    def enable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))


class Miscellaneous(models.Model):
    service = models.ForeignKey(MiscService, verbose_name=_("service"),
        related_name='instances')
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
        related_name='miscellaneous')
    identifier = NullableCharField(_("identifier"), max_length=256, null=True, unique=True,
        db_index=True, help_text=_("A unique identifier for this service."))
    description = models.TextField(_("description"), blank=True)
    amount = models.PositiveIntegerField(_("amount"), default=1)
    is_active = models.BooleanField(_("active"), default=True,
        help_text=_("Designates whether this service should be treated as "
                    "active. Unselect this instead of deleting services."))
    
    class Meta:
        verbose_name_plural = _("miscellaneous")
    
    def __str__(self):
        return self.identifier or self.description[:32] or str(self.service)
    
    @cached_property
    def active(self):
        return self.is_active and self.service.is_active and self.account.is_active
    
    def get_description(self):
        return ' '.join((str(self.amount), self.service.description or self.service.verbose_name))
    
    def disable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
    
    def enable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
    
    @cached_property
    def service_class(self):
        return self.service
    
    def clean(self):
        if self.identifier:
            self.identifier = self.identifier.strip()
        self.description = self.description.strip()
