from copy import deepcopy

from admin_tools.menu import items, Menu
from django.core.urlresolvers import reverse
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services, accounts, administration


def api_link(context):
    """ Dynamically generates API related URL """
    if 'opts' in context:
        opts = context['opts']
    elif 'cl' in context:
        opts = context['cl'].opts
    else:
        return reverse('api-root')
    if 'object_id' in context: 
        object_id = context['object_id']
        try:
            return reverse('%s-detail' % opts.model_name, args=[object_id])
        except:
            return reverse('api-root')
    try:
        return reverse('%s-list' % opts.model_name)
    except:
        return reverse('api-root')


def process_registry(register):
    def get_item(model, options, parent=False):
        name = options.get('verbose_name_plural')
        if isinstance(model, str):
            url = reverse('admin:'+model)
        else:
            opts = model._meta
            url = reverse('admin:{}_{}_changelist'.format(
                opts.app_label, opts.model_name))
            if parent:
                name = opts.app_label
        name = capfirst(name)
        return items.MenuItem(name, url)
    
    childrens = {}
    for model, options in register.get().items():
        if options.get('menu', True):
            parent = options.get('parent')
            if parent:
                parent_item = childrens.get(parent)
                if parent_item:
                    if not parent_item.children:
                        parent_item.children.append(deepcopy(parent_item))
                else:
                    parent_item = get_item(parent, register[parent], parent=True)
                    parent_item.children = []
                parent_item.children.append(get_item(model, options))
                childrens[parent] = parent_item
            elif model not in childrens:
                childrens[model] = get_item(model, options)
            else:
                childrens[model].children.insert(0, get_item(model, options))
    return sorted(childrens.values(), key=lambda i: i.title)


class OrchestraMenu(Menu):
    template = 'admin/orchestra/menu.html'
    
    def init_with_context(self, context):
        self.children = [
#            items.MenuItem(
#                mark_safe('{site_name} <span style="{version_style}">v{version}</span>'.format(
#                    site_name=force_text(settings.SITE_VERBOSE_NAME),
#                    version_style="text-transform:none; float:none; font-size:smaller; background:none;",
#                    version=get_version())),
#                reverse('admin:index')
#            ),
#            items.MenuItem(
#                _('Dashboard'),
#                reverse('admin:index')
#            ),
#            items.Bookmarks(),
            items.MenuItem(
                _("Services"),
                children=process_registry(services)
            ),
            items.MenuItem(
                _("Accounts"),
                reverse('admin:accounts_account_changelist'),
                children=process_registry(accounts)
            ),
            items.MenuItem(
                _("Administration"),
                children=process_registry(administration)
            ),
            items.MenuItem("API", api_link(context)),
        ]
