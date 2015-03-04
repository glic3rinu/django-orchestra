from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.accounts.admin import AccountAdminMixin
from orchestra.plugins.admin import SelectPluginAdminMixin

from .models import SaaS
from .services import SoftwareService


class SaaSAdmin(SelectPluginAdminMixin, AccountAdminMixin, admin.ModelAdmin):
    list_display = ('username', 'service', 'display_site_name', 'account_link')
    list_filter = ('service',)
    plugin = SoftwareService
    plugin_field = 'service'
    plugin_title = 'Software as a Service'
    
    def display_site_name(self, saas):
        site_name = saas.get_site_name()
        return '<a href="http://%s">%s</a>' % (site_name, site_name)
    display_site_name.short_description = _("Site name")
    display_site_name.allow_tags = True
    display_site_name.admin_order_field = 'site_name'


admin.site.register(SaaS, SaaSAdmin)
