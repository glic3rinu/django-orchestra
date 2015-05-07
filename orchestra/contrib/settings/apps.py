from django.apps import AppConfig
from django.core.checks import register, Error
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext, ugettext_lazy as _

from orchestra.core import administration

from . import Setting


class SettingsConfig(AppConfig):
    name = 'orchestra.contrib.settings'
    verbose_name = 'Settings'
    
    def ready(self):
        administration.register_view('settings_setting_change', verbose_name=_("Setting"),
            verbose_name_plural=_("Settings"),
            icon='Multimedia-volume-control.png')
    
    @register()
    def check_settings(app_configs, **kwargs):
        """ perfroms all the validation """
        messages = []
        for name, setting in Setting.settings.items():
            try:
                setting.validate_value(setting.value)
            except ValidationError as exc:
                msg = "Error validating setting with value %s: %s" % (setting.value, str(exc))
                messages.append(Error(msg, obj=name, id='settings.E001'))
        return messages
