import os
from collections import OrderedDict

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField

from orchestra.core import validators

from . import settings
from .fields import VirtualDatabaseRelation, VirtualDatabaseUserRelation
from .options import AppOption
from .types import AppType


class WebApp(models.Model):
    """ Represents a web application """
    name = models.CharField(_("name"), max_length=128, validators=[validators.validate_name],
        help_text=_("The app will be installed in %s") % settings.WEBAPPS_BASE_DIR)
    type = models.CharField(_("type"), max_length=32, choices=AppType.get_choices())
    account = models.ForeignKey('accounts.Account', verbose_name=_("Account"),
        related_name='webapps')
    data = JSONField(_("data"), blank=True, default={},
        help_text=_("Extra information dependent of each service."))
    target_server = models.ForeignKey('orchestration.Server', verbose_name=_("Target Server"),
        related_name='webapps')
    comments = models.TextField(default="", blank=True)
    
    # CMS webapps usually need a database and dbuser, with these virtual fields we tell the ORM to delete them
    databases = VirtualDatabaseRelation('databases.Database')
    databaseusers = VirtualDatabaseUserRelation('databases.DatabaseUser')
    
    class Meta:
        unique_together = ('name', 'account')
        verbose_name = _("Web App")
        verbose_name_plural = _("Web Apps")
    
    def __str__(self):
        return self.name
    
    def get_description(self):
        return self.get_type_display()
    
    @cached_property
    def type_class(self):
        return AppType.get(self.type)
    
    @cached_property
    def type_instance(self):
        """ Per request lived type_instance """
        return self.type_class(self)
    
    def clean(self):
        apptype = self.type_instance
        apptype.validate()
        a = apptype.clean_data()
        self.data = apptype.clean_data()
    
    def get_options(self, **kwargs):
        options = OrderedDict()
        qs = WebAppOption.objects.filter(**kwargs)
        for name, value in qs.values_list('name', 'value').order_by('name'):
            if name in options:
                if AppOption.get(name).comma_separated:
                    options[name] = options[name].rstrip(',') + ',' + value.lstrip(',')
                else:
                    options[name] = max(options[name], value)
            else:
                options[name] = value
        return options
    
    def get_directive(self):
        return self.type_instance.get_directive()
    
    def get_base_path(self):
        context = {
            'home': self.get_user().get_home(),
            'app_name': self.name,
        }
        return settings.WEBAPPS_BASE_DIR % context
    
    def get_path(self):
        path = self.get_base_path()
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
    name = models.CharField(_("name"), max_length=128,
        choices=AppType.get_group_options_choices())
    value = models.CharField(_("value"), max_length=256)
    
    class Meta:
        unique_together = ('webapp', 'name')
        verbose_name = _("option")
        verbose_name_plural = _("options")
    
    def __str__(self):
        return self.name
    
    @cached_property
    def option_class(self):
        return AppOption.get(self.name)
    
    @cached_property
    def option_instance(self):
        """ Per request lived option instance """
        return self.option_class(self)
    
    def clean(self):
        self.option_instance.validate()
