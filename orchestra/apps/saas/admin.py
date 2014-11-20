from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.accounts.admin import AccountAdminMixin
from orchestra.apps.plugins.admin import SelectPluginAdminMixin

from .models import SaaS
from .services import SoftwareService


class SaaSAdmin(SelectPluginAdminMixin, AccountAdminMixin, admin.ModelAdmin):
    list_display = ('username', 'service', 'display_site_name', 'account_link')
    list_filter = ('service',)
    plugin = SoftwareService
    plugin_field = 'service'
    
    def display_site_name(self, saas):
        site_name = saas.get_site_name()
        return '<a href="http://%s">%s</a>' % (site_name, site_name)
    display_site_name.short_description = _("Site name")
    display_site_name.allow_tags = True
    display_site_name.admin_order_field = 'site_name'
    
    def get_fields(self, request, obj=None):
        fields = super(SaaSAdmin, self).get_fields(request, obj)
        fields = list(fields)
        # TODO do it in AccountAdminMixin?
        if obj is not None:
            fields.remove('account')
        else:
            fields.remove('account_link')
        return fields

admin.site.register(SaaS, SaaSAdmin)
