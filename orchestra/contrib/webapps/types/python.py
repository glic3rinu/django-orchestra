import re

from django import forms
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orchestra.plugins.forms import PluginDataForm

from .. import settings
from ..options import AppOption

from . import AppType


help_message = _("Version of Python used to execute this webapp. <br>"
    "Changing the Python version may result in application malfunction, "
    "make sure that everything continue to work as expected.")


class PythonAppForm(PluginDataForm):
    python_version = forms.ChoiceField(label=_("Python version"),
        choices=settings.WEBAPPS_PYTHON_VERSIONS,
        initial=settings.WEBAPPS_DEFAULT_PYTHON_VERSION,
        help_text=help_message)


class PythonAppSerializer(serializers.Serializer):
    python_version = serializers.ChoiceField(label=_("Python version"),
        choices=settings.WEBAPPS_PYTHON_VERSIONS,
        default=settings.WEBAPPS_DEFAULT_PYTHON_VERSION,
        help_text=help_message)


class PythonApp(AppType):
    name = 'python'
    verbose_name = "Python"
    help_text = _("This creates a Python application under ~/webapps/&lt;app_name&gt;<br>")
    form = PythonAppForm
    serializer = PythonAppSerializer
    option_groups = (AppOption.FILESYSTEM, AppOption.PROCESS)
    icon = 'orchestra/icons/apps/Python.png'
    
    @classmethod
    def get_detail_lookups(cls):
        return {
            'python_version': settings.WEBAPPS_PYTHON_VERSIONS,
        }
    
    def get_directive(self):
        context = self.get_directive_context()
        return ('uwsgi', settings.WEBAPPS_UWSGI_SOCKET % context)
    
    def get_python_version(self):
        default_version = self.DEFAULT_PYTHON_VERSION
        return self.instance.data.get('python_version', default_version)
    
    def get_python_version_number(self):
        python_version = self.get_python_version()
        number = re.findall(r'[0-9]+\.?[0-9]?', python_version)
        if not number:
            raise ValueError("No version number matches for '%s'" % python_version)
        if len(number) > 1:
            raise ValueError("Multiple version number matches for '%s'" % python_version)
        return number[0]
