import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from orchestra.core import validators, services
from orchestra.utils.functional import cached

from . import settings, options
from .types import AppType


class WebApp(models.Model):
    """ Represents a web application """
    name = models.CharField(_("name"), max_length=128, validators=[validators.validate_name])
    type = models.CharField(_("type"), max_length=32,
            choices=AppType.get_plugin_choices())
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='webapps')
    data = JSONField(_("data"), help_text=_("Extra information dependent of each service."))
    
    class Meta:
        unique_together = ('name', 'account')
        verbose_name = _("Web App")
        verbose_name_plural = _("Web Apps")
    
    def __unicode__(self):
        return self.name
    
    def get_description(self):
        return self.get_type_display()
    
    @cached_property
    def type_class(self):
        return AppType.get_plugin(self.type)
    
    @cached_property
    def type_instance(self):
        """ Per request lived type_instance """
        return self.type_class()
    
    def clean(self):
        apptype = self.type_instance
        apptype.validate(self)
        self.data = apptype.clean_data(self)
    
    @cached
    def get_options(self):
        return {
            opt.name: opt.value for opt in self.options.all()
        }
    
    @property
    def app_type(self):
        return settings.WEBAPPS_TYPES[self.type]
    
    def get_fpm_port(self):
        return settings.WEBAPPS_FPM_START_PORT + self.account_id
    
    def get_directive(self):
        directive = self.app_type['directive']
        args = directive[1:] if len(directive) > 1 else ()
        return directive[0], args
    
    def get_path(self):
        context = {
            'home': self.get_user().get_home(),
            'app_name': self.name,
        }
        path = settings.WEBAPPS_BASE_ROOT % context
        return path.replace('//', '/')
    
    def get_user(self):
        return self.account.main_systemuser
    
    def get_username(self):
        return self.get_user().username
    
    def get_groupname(self):
        return self.get_username()


class WebAppOption(models.Model):
    webapp = models.ForeignKey(WebApp, verbose_name=_("Web application"),
            related_name='options')
    name = models.CharField(_("name"), max_length=128,
            choices=((op.name, op.verbose_name) for op in options.get_enabled().values()))
    value = models.CharField(_("value"), max_length=256)
    
    class Meta:
        unique_together = ('webapp', 'name')
        verbose_name = _("option")
        verbose_name_plural = _("options")
    
    def __unicode__(self):
        return self.name
    
    def clean(self):
        option = options.get_enabled()[self.name]
        option.validate(self)


services.register(WebApp)


# Admin bulk deletion doesn't call model.delete(), we use signals instead of model method overriding

from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver

@receiver(pre_save, sender=WebApp, dispatch_uid='webapps.type.save')
def type_save(sender, *args, **kwargs):
    instance = kwargs['instance']
    instance.type_instance.save(instance)

@receiver(pre_delete, sender=WebApp, dispatch_uid='webapps.type.delete')
def type_delete(sender, *args, **kwargs):
    instance = kwargs['instance']
    instance.type_instance.delete(instance)
