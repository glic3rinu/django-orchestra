from django import forms
from django.utils.translation import ugettext_lazy as _

from orchestra.utils import plugins
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from .. import settings


class SoftwareService(plugins.Plugin):
    description_field = ''
    form = None
    serializer = None
    icon = 'orchestra/icons/apps.png'
    class_verbose_name = _("Software as a Service")
    
    @classmethod
    @cached
    def get_plugins(cls):
        plugins = []
        for cls in settings.SAAS_ENABLED_SERVICES:
            plugins.append(import_class(cls))
        return plugins
    
    def get_form(self):
        self.form.plugin = self
        self.form.plugin_field = 'service'
        return self.form
    
    def get_serializer(self):
        self.serializer.plugin = self
        return self.serializer
    
    def get_description(self, data):
        return data[self.description_field]
