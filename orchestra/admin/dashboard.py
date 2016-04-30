from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from fluent_dashboard import dashboard, appsettings
from fluent_dashboard.modules import CmsAppIconList

from orchestra.core import services, accounts, administration


class AppDefaultIconList(CmsAppIconList):
    """ Provides support for custom default icons """
    def __init__(self, *args, **kwargs):
        self.icons = kwargs.pop('icons')
        super(AppDefaultIconList, self).__init__(*args, **kwargs)
    
    def get_icon_for_model(self, app_name, model_name, default=None):
        icon = self.icons.get('.'.join((app_name, model_name)))
        return super(AppDefaultIconList, self).get_icon_for_model(app_name, model_name, default=icon)


class OrchestraIndexDashboard(dashboard.FluentIndexDashboard):
    """ Gets application modules from services, accounts and administration registries """
    
    def __init__(self, **kwargs):
        super(dashboard.FluentIndexDashboard, self).__init__(**kwargs)
        self.children.append(self.get_personal_module())
        self.children.extend(self.get_application_modules())
        recent_actions = self.get_recent_actions_module()
        recent_actions.enabled = True
        self.children.append(recent_actions)
    
    def process_registered_view(self, module, view_name, options):
        app_name, name = view_name.split('_')[:-1]
        module.icons['.'.join((app_name, name))] = options.get('icon')
        url = reverse('admin:' + view_name)
        add_url = '/'.join(url.split('/')[:-2])
        module.children.append({
            'models': [
                {
                    'add_url': add_url,
                    'app_name': app_name,
                    'change_url': url,
                    'name': name,
                    'title': options.get('verbose_name_plural')
                }
            ],
            'name': app_name,
            'title': options.get('verbose_name_plural'),
            'url': add_url,
        })
    
    def get_application_modules(self):
        modules = []
        # Honor settings override, hacky. I Know
        if appsettings.FLUENT_DASHBOARD_APP_GROUPS[0][0] != _('CMS'):
            modules = super(OrchestraIndexDashboard, self).get_application_modules()
        for register in (accounts, services, administration):
            title = register.verbose_name
            models = []
            icons = {}
            views = []
            for model, options in register.get().items():
                if isinstance(model, str):
                    views.append((model, options))
                elif options.get('dashboard', True):
                    opts = model._meta
                    label = "%s.%s" % (model.__module__, opts.object_name)
                    models.append(label)
                    label = '.'.join((opts.app_label, opts.model_name))
                    icons[label] = options.get('icon')
            module = AppDefaultIconList(title, models=models, icons=icons, collapsible=True)
            for view_name, options in views:
                self.process_registered_view(module, view_name, options)
            modules.append(module)
        return modules
