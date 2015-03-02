import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators, services
from orchestra.utils import tuple_setting_to_choices, dict_setting_to_choices
from orchestra.utils.functional import cached

from . import settings


class WebApp(models.Model):
    """ Represents a web application """
    name = models.CharField(_("name"), max_length=128, validators=[validators.validate_name])
    type = models.CharField(_("type"), max_length=32,
            choices=dict_setting_to_choices(settings.WEBAPPS_TYPES),
            default=settings.WEBAPPS_DEFAULT_TYPE)
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='webapps')
    
    class Meta:
        unique_together = ('name', 'account')
        verbose_name = _("Web App")
        verbose_name_plural = _("Web Apps")
    
    def __unicode__(self):
        return self.name
    
    def get_description(self):
        return self.get_type_display()
    
    def clean(self):
        # Validate unique webapp names
        if self.app_type.get('unique_name', False):
            try:
                webapp = WebApp.objects.exclude(id=self.pk).get(name=self.name, type=self.type)
            except WebApp.DoesNotExist:
                pass
            else:
                raise ValidationError({
                    'name': _("A webapp with this name already exists."),
                })
    
    @cached
    def get_options(self):
        return { opt.name: opt.value for opt in self.options.all() }
    
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
            choices=tuple_setting_to_choices(settings.WEBAPPS_OPTIONS))
    value = models.CharField(_("value"), max_length=256)
    
    class Meta:
        unique_together = ('webapp', 'name')
        verbose_name = _("option")
        verbose_name_plural = _("options")
    
    def __unicode__(self):
        return self.name
    
    def clean(self):
        """ validates name and value according to WEBAPPS_OPTIONS """
        regex = settings.WEBAPPS_OPTIONS[self.name][-1]
        if not re.match(regex, self.value):
            raise ValidationError({
                'value': ValidationError(_("'%(value)s' does not match %(regex)s."),
                    params={
                        'value': self.value,
                        'regex': regex
                    }),
            })


services.register(WebApp)
