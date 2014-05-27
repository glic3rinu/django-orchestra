from admin_tools.menu import items, Menu
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services
from orchestra.utils.apps import isinstalled


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
            return reverse('%s-detail' % opts.module_name, args=[object_id])
        except:
            return reverse('api-root')
    try:
        return reverse('%s-list' % opts.module_name)
    except:
        return reverse('api-root')


def get_services():
    result = []
    for model, options in services.get().iteritems():
        if options.get('menu', True):
            opts = model._meta
            url = reverse('admin:%s_%s_changelist' % (opts.app_label, opts.model_name))
            result.append(items.MenuItem(options.get('verbose_name_plural'), url))
    return sorted(result, key=lambda i: i.title)


def get_accounts():
    accounts = [
        items.MenuItem(_("Accounts"), reverse('admin:accounts_account_changelist'))
    ]
    if isinstalled('orchestra.apps.contacts'):
        url = reverse('admin:contacts_contact_changelist')
        accounts.append(items.MenuItem(_("Contacts"), url))
    if isinstalled('orchestra.apps.users'):
        url = reverse('admin:users_user_changelist')
        users = [items.MenuItem(_("Users"), url)]
        if isinstalled('rest_framework.authtoken'):
            tokens = reverse('admin:authtoken_token_changelist')
            users.append(items.MenuItem(_("Tokens"), tokens))
        accounts.append(items.MenuItem(_("Users"), url, children=users))
    if isinstalled('orchestra.apps.prices'):
        url = reverse('admin:prices_price_changelist')
        accounts.append(items.MenuItem(_("Prices"), url))
    if isinstalled('orchestra.apps.orders'):
        url = reverse('admin:orders_order_changelist')
        accounts.append(items.MenuItem(_("Orders"), url))
    return accounts


def get_administration():
    administration = []
    return administration


def get_administration_models():
    administration_models = []
    if isinstalled('orchestra.apps.orchestration'):
        administration_models.append('orchestra.apps.orchestration.*')
    if isinstalled('djcelery'):
        administration_models.append('djcelery.*')
    if isinstalled('orchestra.apps.issues'):
        administration_models.append('orchestra.apps.issues.*')
    return administration_models


class OrchestraMenu(Menu):
    def init_with_context(self, context):
        self.children += [
            items.MenuItem(
                _('Dashboard'),
                reverse('admin:index')
            ),
            items.Bookmarks(),
            items.MenuItem(
                _("Services"),
                reverse('admin:index'),
                children=get_services()
            ),
            items.MenuItem(
                _("Accounts"),
                reverse('admin:accounts_account_changelist'),
                children=get_accounts()
            ),
            items.AppList(
                _("Administration"),
                models=get_administration_models(),
                children=get_administration()
            ),
            items.MenuItem("API", api_link(context))
        ]
