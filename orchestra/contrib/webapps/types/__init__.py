import importlib
import os
from functools import lru_cache

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra import plugins
from orchestra.plugins.forms import PluginDataForm
from orchestra.utils.python import import_class

from .. import settings
from ..options import AppOption


class AppType(plugins.Plugin, metaclass=plugins.PluginMount):
    name = None
    verbose_name = ""
    help_text= ""
    form = PluginDataForm
    icon = 'orchestra/icons/apps.png'
    unique_name = False
    option_groups = (AppOption.FILESYSTEM, AppOption.PROCESS, AppOption.PHP)
    plugin_field = 'type'
    # TODO generic name like 'execution' ?
    
    @classmethod
    @lru_cache()
    def get_plugins(cls, all=False):
        if all:
            for module in os.listdir(os.path.dirname(__file__)):
                if module != '__init__.py' and module[-3:] == '.py':
                    importlib.import_module('.'+module[:-3], __package__)
            plugins = super().get_plugins()
        else:
            plugins = []
            for cls in settings.WEBAPPS_TYPES:
                plugins.append(import_class(cls))
        return plugins
    
    def validate(self):
        """ Unique name validation """
        if self.unique_name:
            if not self.instance.pk and type(self.instance).objects.filter(name=self.instance.name, type=self.instance.type).exists():
                raise ValidationError({
                    'name': _("A WordPress blog with this name already exists."),
                })
    
    @classmethod
    @lru_cache()
    def get_group_options(cls):
        """ Get enabled options based on cls.option_groups """
        groups = AppOption.get_option_groups()
        options = []
        for group in cls.option_groups:
            group_options = groups[group]
            if group is None:
                options.insert(0, (group, group_options))
            else:
                options.append((group, group_options))
        return options
    
    @classmethod
    def get_group_options_choices(cls):
        """ Generates grouped choices ready to use in Field.choices """
        # generators can not be @lru_cache
        yield (None, '-------')
        for group, options in cls.get_group_options():
            if group is None:
                for option in options:
                    yield (option.name, option.verbose_name)
            else:
                yield (group, [(op.name, op.verbose_name) for op in options])
    
    @classmethod
    def get_detail_lookups(cls):
        """ {'field_name': (('opt1', _("Option 1"),)} """
        return {}
    
    def get_detail(self):
        return ''
    
    def save(self):
        pass
    
    def delete(self):
        pass
    
    def get_directive_context(self):
        return {
            'app_id': self.instance.id,
            'app_name': self.instance.name,
            'user': self.instance.get_username(),
            'user_id': self.instance.account.main_systemuser_id,
            'home': self.instance.account.main_systemuser.get_home(),
            'account_id': self.instance.account_id,
        }
