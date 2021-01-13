from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from orchestra.core import validators

from .fields import VirtualDatabaseRelation
from .services import SoftwareService


class SaaSQuerySet(models.QuerySet):
    def create(self, **kwargs):
        """ Sets password if provided, all within a single DB operation """
        password = kwargs.pop('password')
        saas = SaaS(**kwargs)
        if password:
            saas.set_password(password)
        saas.save()
        return saas


class SaaS(models.Model):
    service = models.CharField(_("service"), max_length=32,
        choices=SoftwareService.get_choices())
    name = models.CharField(_("Name"), max_length=64,
        help_text=_("Required. 64 characters or fewer. Letters, digits and ./- only."),
        validators=[validators.validate_hostname])
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
        related_name='saas')
    is_active = models.BooleanField(_("active"), default=True,
        help_text=_("Designates whether this service should be treated as active. "))
    data = JSONField(_("data"), default={},
        help_text=_("Extra information dependent of each service."))
    custom_url = models.URLField(_("custom URL"), blank=True,
        help_text=_("Optional and alternative URL for accessing this service instance. "
                    "i.e. <tt>https://wiki.mydomain/doku/</tt><br>"
                    "A related website will be automatically configured if needed."))
    database = models.ForeignKey('databases.Database', null=True, blank=True)
    
    # Some SaaS sites may need a database, with this virtual field we tell the ORM to delete them
    databases = VirtualDatabaseRelation('databases.Database')
    objects = SaaSQuerySet.as_manager()
    
    class Meta:
        verbose_name = "SaaS"
        verbose_name_plural = "SaaS"
        unique_together = (
            ('name', 'service'),
        )
    
    def __str__(self):
        return "%s@%s" % (self.name, self.service)
    
    @cached_property
    def service_class(self):
        return SoftwareService.get(self.service)
    
    @cached_property
    def service_instance(self):
        """ Per request lived service_instance """
        return self.service_class(self)
    
    @cached_property
    def active(self):
        return self.is_active and self.account.is_active
    
    def disable(self):
        self.is_active = False
        self.save(update_fields=('is_active',))
    
    def enable(self):
        self.is_active = True
        self.save(update_fields=('is_active',))
    
    def clean(self):
        if not self.pk:
            self.name = self.name.lower()
        self.service_instance.clean()
        self.data = self.service_instance.clean_data()
    
    def get_site_domain(self):
        return self.service_instance.get_site_domain()
    
    def set_password(self, password):
        self.password = password
