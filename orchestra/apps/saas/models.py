from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from orchestra.core import services, validators
from orchestra.models.fields import NullableCharField

from .services import SoftwareService


class SaaS(models.Model):
    service = models.CharField(_("service"), max_length=32,
            choices=SoftwareService.get_plugin_choices())
    username = models.CharField(_("username"), max_length=64,
            help_text=_("Required. 64 characters or fewer. Letters, digits and ./-/_ only."),
            validators=[validators.validate_username])
    site_name = NullableCharField(_("site name"), max_length=32, null=True)
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='saas')
    data = JSONField(_("data"), help_text=_("Extra information dependent of each service."))
    
    class Meta:
        verbose_name = "SaaS"
        verbose_name_plural = "SaaS"
        unique_together = (
            ('username', 'service'),
            ('site_name', 'service'),
        )
    
    def __unicode__(self):
        return "%s@%s" % (self.username, self.service)
    
    @cached_property
    def service_class(self):
        return SoftwareService.get_plugin(self.service)
    
    def get_site_name(self):
        return self.service_class().get_site_name(self)
    
    def clean(self):
        self.data = self.service_class().clean_data(self)
    
    def set_password(self, password):
        self.password = password

services.register(SaaS)
