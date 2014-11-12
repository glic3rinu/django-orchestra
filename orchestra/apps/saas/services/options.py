from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra.apps import plugins
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from .. import settings


# TODO if unique_description: make description_field create only
class SoftwareService(plugins.Plugin):
    description_field = ''
    unique_description = True
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
    
    @classmethod
    def clean_data(cls, saas):
        """ model clean, uses cls.serizlier by default """
        if cls.unique_description and not saas.pk:
            from ..models import SaaS
            field = cls.description_field
            if SaaS.objects.filter(data__contains='"%s":"%s"' % (field, saas.data[field])).exists():
                raise ValidationError({
                    field: _("SaaS service with this %(field)s already exists.")
                }, params={'field': field})
        serializer = cls.serializer(data=saas.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        return serializer.data
    
    def get_form(self):
        self.form.plugin = self
        self.form.plugin_field = 'service'
        return self.form
    
    def get_serializer(self):
        self.serializer.plugin = self
        return self.serializer
    
    def get_description(self, data):
        return data[self.description_field]
