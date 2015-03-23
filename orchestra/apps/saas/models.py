from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from orchestra.core import services, validators
from orchestra.models.fields import NullableCharField

from .services import SoftwareService


class SaaS(models.Model):
    service = models.CharField(_("service"), max_length=32,
            choices=SoftwareService.get_plugin_choices())
    username = models.CharField(_("name"), max_length=64,
            help_text=_("Required. 64 characters or fewer. Letters, digits and ./-/_ only."),
            validators=[validators.validate_username])
#    site_name = NullableCharField(_("site name"), max_length=32, null=True)
    account = models.ForeignKey('accounts.Account', verbose_name=_("account"),
            related_name='saas')
    data = JSONField(_("data"), default={},
            help_text=_("Extra information dependent of each service."))
    
    class Meta:
        verbose_name = "SaaS"
        verbose_name_plural = "SaaS"
        unique_together = (
            ('username', 'service'),
#            ('site_name', 'service'),
        )
    
    def __unicode__(self):
        return "%s@%s" % (self.username, self.service)
    
    @cached_property
    def service_class(self):
        return SoftwareService.get_plugin(self.service)
    
    @cached_property
    def service_instance(self):
        """ Per request lived service_instance """
        return self.service_class(self)
    
    def get_site_name(self):
        return self.service_instance.get_site_name()
    
    def clean(self):
        self.data = self.service_instance.clean_data()
    
    def set_password(self, password):
        self.password = password


services.register(SaaS)


# Admin bulk deletion doesn't call model.delete()
# So, signals are used instead of model method overriding

@receiver(pre_save, sender=SaaS, dispatch_uid='saas.service.save')
def type_save(sender, *args, **kwargs):
    instance = kwargs['instance']
    instance.service_instance.save()

@receiver(pre_delete, sender=SaaS, dispatch_uid='saas.service.delete')
def type_delete(sender, *args, **kwargs):
    instance = kwargs['instance']
    try:
        instance.service_instance.delete()
    except KeyError:
        pass
