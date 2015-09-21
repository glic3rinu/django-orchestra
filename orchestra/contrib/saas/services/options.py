from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from orchestra import plugins
from orchestra.contrib.orchestration import Operation
from orchestra.utils.functional import cached
from orchestra.utils.python import import_class

from .. import settings
from ..forms import SaaSPasswordForm


class SoftwareService(plugins.Plugin):
    form = SaaSPasswordForm
    site_domain = None
    site_base_domain = None
    has_custom_domain = False
    icon = 'orchestra/icons/apps.png'
    class_verbose_name = _("Software as a Service")
    plugin_field = 'service'
    
    @classmethod
    @cached
    def get_plugins(cls):
        plugins = []
        for cls in settings.SAAS_ENABLED_SERVICES:
            plugins.append(import_class(cls))
        return plugins
    
    def get_change_readonly_fileds(cls):
        fields = super(SoftwareService, cls).get_change_readonly_fileds()
        return fields + ('name',)
    
    def get_site_domain(self):
        return self.site_domain or '.'.join(
            (self.instance.name, self.site_base_domain)
        )
    
    def clean_data(self):
        data = super(SoftwareService, self).clean_data()
        if not self.instance.pk:
            try:
                log = Operation.execute_action(self.instance, 'validate_creation')[0]
            except IndexError:
                pass
            else:
                if log.state != log.SUCCESS:
                    raise ValidationError(_("Validate creation execution has failed."))
                errors = {}
                if 'user-exists' in log.stdout:
                    errors['name'] = _("User with this username already exists.")
                if 'email-exists' in log.stdout:
                    errors['email'] = _("User with this email address already exists.")
                if errors:
                    raise ValidationError(errors)
        return data
    
    def save(self):
        pass
    
    def delete(self):
        pass
    
    def get_related(self):
        return []
