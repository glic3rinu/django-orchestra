from django.core.urlresolvers import reverse
from fluent_dashboard import dashboard
from fluent_dashboard.modules import CmsAppIconList

from orchestra.core import services


class OrchestraIndexDashboard(dashboard.FluentIndexDashboard):
    _registry = {}
    
    @classmethod
    def register_link(cls, module, view_name, title):
        registered = cls._registry.get(module, [])
        registered.append((view_name, title))
        cls._registry[module] = registered
    
    def get_application_modules(self):
        modules = super(OrchestraIndexDashboard, self).get_application_modules()
        models = []
        for model, options in services.get().items():
            if options.get('menu', True):
                models.append("%s.%s" % (model.__module__, model._meta.object_name))
        
        for module in modules:
            registered = self._registry.get(module.title, None)
            if registered:
                for view_name, title in registered:
                    # This values are shit, but it is how fluent dashboard will look for the icon
                    app_name, name = view_name.split('_')[:-1]
                    url = reverse('admin:' + view_name)
                    add_url = '/'.join(url.split('/')[:-2])
                    module.children.append({
                        'models': [{
                            'add_url': add_url,
                            'app_name': app_name,
                            'change_url': url,
                            'name': name,
                            'title': title }],
                       'name': app_name,
                       'title': title,
                       'url': add_url,
                    })
        service_icon_list = CmsAppIconList('Services', models=models, collapsible=True)
        modules.append(service_icon_list)
        return modules
