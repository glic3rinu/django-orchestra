import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.core import validators, services
from orchestra.utils.functional import cached

from . import settings


def settings_to_choices(choices):
    return sorted(
        [ (name, opt[0]) for name,opt in choices.iteritems() ],
        key=lambda e: e[0]
    )


class WebApp(models.Model):
    """ Represents a web application """
    name = models.CharField(_("name"), max_length=128, validators=[validators.validate_name])
    type = models.CharField(_("type"), max_length=32,
            choices=settings_to_choices(settings.WEBAPPS_TYPES),
            default=settings.WEBAPPS_DEFAULT_TYPE)
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
            related_name='webapps')
    
    class Meta:
        unique_together = ('name', 'account')
        verbose_name = _("Web App")
        verbose_name_plural = _("Web Apps")
    
    def __unicode__(self):
        return self.name
    
    @cached
    def get_options(self):
        return { opt.name: opt.value for opt in self.options.all() }
    
    def get_fpm_port(self):
        return settings.WEBAPPS_FPM_START_PORT + self.account.pk
    
    def get_method(self):
        method = settings.WEBAPPS_TYPES[self.type]
        args = method[2] if len(method) == 4 else ()
        return method[1], args
    
    def get_path(self):
        context = {
            'user': self.account.username,
            'app_name': self.name,
        }
        return settings.WEBAPPS_BASE_ROOT % context
    
    def get_username(self):
        return self.account.username
    
    def get_groupname(self):
        return self.get_username()


class WebAppOption(models.Model):
    webapp = models.ForeignKey(WebApp, verbose_name=_("Web application"),
            related_name='options')
    name = models.CharField(_("name"), max_length=128,
            choices=settings_to_choices(settings.WEBAPPS_OPTIONS))
    value = models.CharField(_("value"), max_length=256)
    
    class Meta:
        unique_together = ('webapp', 'name')
        verbose_name = _("option")
        verbose_name_plural = _("options")
    
    def __unicode__(self):
        return self.name
    
    def clean(self):
        """ validates name and value according to WEBAPPS_OPTIONS """
        __, regex = settings.WEBAPPS_OPTIONS[self.name]
        if not re.match(regex, self.value):
            msg = _("'%s' does not match %s")
            raise ValidationError(msg % (self.value, regex))


services.register(WebApp)
