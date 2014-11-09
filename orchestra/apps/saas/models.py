from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from orchestra.core import services

from .services import SoftwareService


class SaaS(models.Model):
    service = models.CharField(_("service"), max_length=32,
            choices=SoftwareService.get_plugin_choices())
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='saas')
    data = JSONField(_("data"))
    
    class Meta:
        verbose_name = "SaaS"
        verbose_name_plural = "SaaS"
    
    def __unicode__(self):
        return "%s (%s)" % (self.description, self.service_class.verbose_name)
    
    @cached_property
    def service_class(self):
        return SoftwareService.get_plugin(self.service)
    
    @cached_property
    def description(self):
        return self.service_class().get_description(self.data)
    
    def clean(self):
        self.data = self.service_class().clean_data(self)


services.register(SaaS)
