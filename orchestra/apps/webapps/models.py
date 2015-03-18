import os
import re

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from orchestra.core import validators, services
from orchestra.utils.functional import cached

from . import settings
from .options import AppOption
from .types import AppType


class WebApp(models.Model):
    """ Represents a web application """
    name = models.CharField(_("name"), max_length=128, validators=[validators.validate_name])
    type = models.CharField(_("type"), max_length=32,
            choices=AppType.get_plugin_choices())
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='webapps')
    data = JSONField(_("data"), blank=True,
            help_text=_("Extra information dependent of each service."))
    
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
        return self.type_class(self)
    
    def clean(self):
        apptype = self.type_instance
        apptype.validate()
        self.data = apptype.clean_data()
    
    @cached
    def get_options(self):
        return {
            opt.name: opt.value for opt in self.options.all()
        }
    
    def get_directive(self):
        return self.type_instance.get_directive()
    
    def get_path(self):
        context = {
            'home': self.get_user().get_home(),
            'app_name': self.name,
        }
        path = settings.WEBAPPS_BASE_ROOT % context
        public_root = self.options.filter(name='public-root').first()
        if public_root:
            path = os.path.join(path, public_root.value)
        return os.path.normpath(path.replace('//', '/'))
    
    def get_user(self):
        return self.account.main_systemuser
    
    def get_username(self):
        return self.get_user().username
    
    def get_groupname(self):
        return self.get_username()


class WebAppOption(models.Model):
    webapp = models.ForeignKey(WebApp, verbose_name=_("Web application"),
            related_name='options')
    name = models.CharField(_("name"), max_length=128, choices=AppType.get_options_choices())
    value = models.CharField(_("value"), max_length=256)
    
    class Meta:
        unique_together = ('webapp', 'name')
        verbose_name = _("option")
        verbose_name_plural = _("options")
    
    def __unicode__(self):
        return self.name
    
    @cached_property
    def option_class(self):
        return AppOption.get_plugin(self.name)
    
    @cached_property
    def option_instance(self):
        """ Per request lived option instance """
        return self.option_class(self)
    
    def clean(self):
        self.option_instance.validate()


services.register(WebApp)


# Admin bulk deletion doesn't call model.delete()
# So, signals are used instead of model method overriding

@receiver(pre_save, sender=WebApp, dispatch_uid='webapps.type.save')
def type_save(sender, *args, **kwargs):
    instance = kwargs['instance']
    instance.type_instance.save()

@receiver(pre_delete, sender=WebApp, dispatch_uid='webapps.type.delete')
def type_delete(sender, *args, **kwargs):
    instance = kwargs['instance']
    try:
        instance.type_instance.delete()
    except KeyError:
        pass
