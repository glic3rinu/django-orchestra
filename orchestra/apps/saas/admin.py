from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.apps.accounts.admin import AccountAdminMixin
from orchestra.plugins.admin import SelectPluginAdminMixin

from .models import SaaS
from .services import SoftwareService


class SaaSAdmin(SelectPluginAdminMixin, AccountAdminMixin, ExtendedModelAdmin):
    list_display = ('name', 'service', 'display_site_domain', 'account_link')
    list_filter = ('service',)
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
