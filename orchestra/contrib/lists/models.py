from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.core.validators import validate_name

from . import settings


class ListQuerySet(models.QuerySet):
    def create(self, **kwargs):
        """ Sets password if provided, all within a single DB operation """
        password = kwargs.pop('password')
        instance = self.model(**kwargs)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# TODO address and domain, perhaps allow only domain?
class List(models.Model):
    name = models.CharField(_("name"), max_length=64, unique=True, validators=[validate_name],
        help_text=_("Default list address &lt;name&gt;@%s") % settings.LISTS_DEFAULT_DOMAIN)
    address_name = models.CharField(_("address name"), max_length=64,
        validators=[validate_name], blank=True)
    address_domain = models.ForeignKey(settings.LISTS_DOMAIN_MODEL, on_delete=models.SET_NULL,
        verbose_name=_("address domain"), blank=True, null=True)
    admin_email = models.EmailField(_("admin email"),
        help_text=_("Administration email address"))
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
        related_name='lists')
    # TODO also admin
    is_active = models.BooleanField(_("active"), default=True,
        help_text=_("Designates whether this account should be treated as active. "
                    "Unselect this instead of deleting accounts."))
    password = None
    
    objects = ListQuerySet.as_manager()
    
    class Meta:
        unique_together = ('address_name', 'address_domain')
    
    def __str__(self):
        return self.name
    
    @property
    def address(self):
        if self.address_name and self.address_domain:
            return "%s@%s" % (self.address_name, self.address_domain)
        return ''
    
    @cached_property
    def active(self):
        return self.is_active and self.account.is_active
    
    def clean(self):
        if self.address_name and not self.address_domain_id:
            raise ValidationError({
                'address_domain': _("Domain should be selected for provided address name."),
            })
    
    def disable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
    
    def enable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
    
    def get_address_name(self):
        return self.address_name or self.name
    
    def get_username(self):
        return self.name
    
    def set_password(self, password):
        self.password = password
    
    def get_absolute_url(self):
        context = {
            'name': self.name
        }
        return settings.LISTS_LIST_URL % context
