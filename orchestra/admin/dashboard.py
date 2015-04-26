from fluent_dashboard import dashboard
from fluent_dashboard.modules import CmsAppIconList

from orchestra.core import services


class OrchestraIndexDashboard(dashboard.FluentIndexDashboard):
    def get_application_modules(self):
        modules = super(OrchestraIndexDashboard, self).get_application_modules()
        models = []
        for model, options in services.get().items():
            if options.get('menu', True):
                models.append("%s.%s" % (model.__module__, model._meta.object_name))
        
        # TODO make this dynamic
        for module in modules:
            if module.title == 'Administration':
                module.children.append({
                    'models': [{
                        'add_url': '/admin/settings/',
                        'app_name': 'settings',
                        'change_url': '/admin/settings/setting/',
                        'name': 'setting',
                        'title': "Settings" }],
                   'name': 'settings',
                   'title': 'Settings',
                   'url': '/admin/settings/'
                })
        service_icon_list = CmsAppIconList('Services', models=models, collapsible=True)
        modules.append(service_icon_list)
        return modules
