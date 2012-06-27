"""
This file was generated with the custommenu management command, it contains
the classes for the admin menu, you can customize this class as you want.

To activate your custom menu add the following to your settings.py::
    ADMIN_TOOLS_MENU = 'orchestra.menu.CustomMenu'
"""

from admin_tools.menu import items, Menu
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
import settings

service_childrens = []

if 'dns' in settings.INSTALLED_APPS:
    service_childrens.append(items.MenuItem('DNS', '/admin/dns/',
        children=[
            items.MenuItem('Names', reverse('admin:dns_name_changelist')),
            items.MenuItem('Zones', reverse('admin:dns_zone_changelist')),
        ]))

if 'web' in settings.INSTALLED_APPS:
    service_childrens.append(items.MenuItem('Web', '/admin/web/',
        children=[
            items.MenuItem('Virtual hosts', reverse('admin:web_virtualhost_changelist')),
            items.MenuItem('System users', reverse('admin:system_users_systemuser_changelist')),
            items.MenuItem('System groups', reverse('admin:system_users_systemgroup_changelist')),
            items.MenuItem('Modules', children = [
                items.MenuItem('PHP', reverse('admin:php_phpdirective_changelist')),
                items.MenuItem('Fcgid', reverse('admin:fcgid_fcgiddirective_changelist')),
                ]),
        ]))

if 'mail' in settings.INSTALLED_APPS:
    service_childrens.append(items.MenuItem('Mail', '/admin/mail/',
        children=[
            items.MenuItem('Virtual users', reverse('admin:mail_virtualuser_changelist')),
            items.MenuItem('Virtual aliases', reverse('admin:mail_virtualaliase_changelist')),
            items.MenuItem('Virtual domains', reverse('admin:mail_virtualdomain_changelist')),
        ]))  

if 'lists' in settings.INSTALLED_APPS:
    service_childrens.append(items.MenuItem('Lists', reverse('admin:lists_list_changelist')),)

if 'vps' in settings.INSTALLED_APPS:
    service_childrens.append(items.MenuItem('VPS', reverse('admin:vps_vps_changelist')),)

if 'jobs' in settings.INSTALLED_APPS:
    service_childrens.append(items.MenuItem('Jobs', '/admin/jobs/',
        children=[
            items.MenuItem('Jobs', reverse('admin:jobs_job_changelist')),                    
            items.MenuItem('Categories', reverse('admin:jobs_category_changelist')),
        ]))  

if 'databases' in settings.INSTALLED_APPS:
    service_childrens.append(items.MenuItem('Databases', '/admin/databases/',
        children=[
            items.MenuItem('Databases', reverse('admin:databases_database_changelist')),
            items.MenuItem('Users', reverse('admin:databases_dbuser_changelist')),
            items.MenuItem('DB', reverse('admin:databases_db_changelist')),
        ]))  

if service_childrens:
    service_menu = items.MenuItem('Services', children=service_childrens)
else: service_menu = None


class CustomMenu(Menu):
    """
    Custom Menu for orchestra admin site.
    """
    def __init__(self, **kwargs):
        Menu.__init__(self, **kwargs)
        self.children += [
            items.MenuItem(_('Dashboard'), reverse('admin:index')),
            items.Bookmarks(),]
            
        if service_menu: 
            self.children.append(service_menu)
        
        self.children.append(items.AppList(
            _('Accountancy'),
            models=('contacts.*.Contact*', 'contacts.*Contract', 'billing.*Bill', 'billing.*Budget', 'payment.*', 'ordering.*.Order', 'ordering.*ServiceAccounting', 'ordering.*.Pack')))
        
        self.children.append(items.AppList(
            _('Administration'),
            models=('django.contrib.*', 'daemons.*', 'djcelery.*', 'resources.*', 'extra_fields.*', 'djangoplugins.*', 'scheduling.*')))

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """

