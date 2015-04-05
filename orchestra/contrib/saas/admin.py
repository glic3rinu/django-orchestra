from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin, ChangePasswordAdminMixin
from orchestra.contrib.accounts.admin import AccountAdminMixin
from orchestra.plugins.admin import SelectPluginAdminMixin

from .models import SaaS
from .services import SoftwareService


class SaaSAdmin(SelectPluginAdminMixin, ChangePasswordAdminMixin, AccountAdminMixin, ExtendedModelAdmin):
    list_display = ('name', 'service', 'display_site_domain', 'account_link', 'is_active')
    list_filter = ('service', 'is_active')
    change_readonly_fields = ('service',)
    plugin = SoftwareService
    plugin_field = 'service'
    plugin_title = 'Software as a Service'
    
    def display_site_domain(self, saas):
        site_domain = saas.get_site_domain()
        return '<a href="http://%s">%s</a>' % (site_domain, site_domain)
    display_site_domain.short_description = _("Site domain")
    display_site_domain.allow_tags = True
    display_site_domain.admin_order_field = 'name'


admin.site.register(SaaS, SaaSAdmin)
