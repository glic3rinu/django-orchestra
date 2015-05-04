from django.apps import AppConfig
from django.core.checks import register, Error
from django.core.exceptions import ValidationError

from . import Setting

class SettingsConfig(AppConfig):
    name = 'orchestra.contrib.settings'
    verbose_name = 'Settings'
    
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
