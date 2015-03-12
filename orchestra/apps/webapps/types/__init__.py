from django.core.exceptions import ValidationError

from orchestra import plugins
from orchestra.plugins.forms import PluginDataForm
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from .. import settings
from ..options import AppOption


class AppType(plugins.Plugin):
    name = None
    verbose_name = ""
    help_text= ""
    form = PluginDataForm
    change_form = None
    serializer = None
    icon = 'orchestra/icons/apps.png'
    unique_name = False
    option_groups = (AppOption.FILESYSTEM, AppOption.PROCESS, AppOption.PHP)
    # TODO generic name like 'execution' ?
    
    @classmethod
    @cached
    def get_plugins(cls):
        plugins = []
        for cls in settings.WEBAPPS_TYPES:
            plugins.append(import_class(cls))
        return plugins
    
    def clean_data(self):
        """ model clean, uses cls.serizlier by default """
        if self.serializer:
            serializer = self.serializer(data=self.instance.data)
            if not serializer.is_valid():
                raise ValidationError(serializer.errors)
            return serializer.data
        return {}
    
    def get_directive(self):
        raise NotImplementedError
    
    def get_form(self):
        self.form.plugin = self
        self.form.plugin_field = 'type'
        return self.form
    
    def get_change_form(self):
        form = self.change_form or self.form
        form.plugin = self
        form.plugin_field = 'type'
        return form
    
    def get_serializer(self):
        self.serializer.plugin = self
        return self.serializer
    
    def validate(self):
        """ Unique name validation """
        if self.unique_name:
            if not self.instance.pk and Webapp.objects.filter(name=self.instance.name, type=self.instance.type).exists():
                raise ValidationError({
                    'name': _("A WordPress blog with this name already exists."),
                })
    
    @classmethod
    @cached
    def get_php_options(cls):
        # TODO validate php options once a php version has been selected (deprecated directives)
        php_version = getattr(cls, 'php_version', 1)
        php_options = AppOption.get_option_groups()[AppOption.PHP]
        return [op for op in php_options if getattr(cls, 'deprecated', 99) > php_version]
    
    @classmethod
    @cached
    def get_options(cls):
        """ Get enabled options based on cls.option_groups """
        groups = AppOption.get_option_groups()
        options = []
        for group in cls.option_groups:
            group_options = groups[group]
            if group == AppOption.PHP:
                group_options = cls.get_php_options()
            if group is None:
                options.insert(0, (group, group_options))
            else:
                options.append((group, group_options))
        return options
    
    @classmethod
    def get_options_choices(cls):
        """ Generates grouped choices ready to use in Field.choices """
        # generators can not be @cached
        yield (None, '-------')
        for group, options in cls.get_options():
            if group is None:
                for option in options:
                    yield (option.name, option.verbose_name)
            else:
                yield (group, [(op.name, op.verbose_name) for op in options])
    
    def save(self):
        pass
    
    def delete(self):
        pass
    
    def get_related_objects(self):
        pass
    
    def get_directive_context(self):
        return {
            'app_id': self.instance.id,
            'app_name': self.instance.name,
            'user': self.instance.account.username,
        }

