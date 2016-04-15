from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin, ChangePasswordAdminMixin
from orchestra.admin.actions import disable, enable
from orchestra.admin.utils import change_url
from orchestra.contrib.accounts.actions import list_accounts
from orchestra.contrib.accounts.admin import AccountAdminMixin
from orchestra.contrib.accounts.filters import IsActiveListFilter
from orchestra.plugins.admin import SelectPluginAdminMixin
from orchestra.utils.apps import isinstalled
from orchestra.utils.html import get_on_site_link

from .filters import CustomURLListFilter
from .models import SaaS
from .services import SoftwareService


class SaaSAdmin(SelectPluginAdminMixin, ChangePasswordAdminMixin, AccountAdminMixin, ExtendedModelAdmin):
    list_display = ('name', 'service', 'display_url', 'account_link', 'display_active')
    list_filter = ('service', IsActiveListFilter, CustomURLListFilter)
    search_fields = ('name', 'account__username')
    change_readonly_fields = ('service',)
    plugin = SoftwareService
    plugin_field = 'service'
    plugin_title = 'Software as a Service'
    actions = (disable, enable, list_accounts)
    
    def display_url(self, saas):
        site_domain = saas.get_site_domain()
        site_link = '<a href="http://%s">%s</a>' % (site_domain, site_domain)
        links = [site_link]
        if saas.custom_url and isinstalled('orchestra.contrib.websites'):
            try:
                website = saas.service_instance.get_website()
            except ObjectDoesNotExist:
                warning = _("Related website directive does not exist for this custom URL.")
                link = '<span style="color:red" title="%s">%s</span>' % (warning, saas.custom_url)
            else:
                website_link = get_on_site_link(saas.custom_url)
                admin_url = change_url(website)
                link = '<a title="Edit website" href="%s">%s %s</a>' % (
                    admin_url, saas.custom_url, website_link
                )
            links.append(link)
        return '<br>'.join(links)
    display_url.short_description = _("URL")
    display_url.allow_tags = True
    display_url.admin_order_field = 'name'
    
    def get_fields(self, *args, **kwargs):
        fields = super(SaaSAdmin, self).get_fields(*args, **kwargs)
        if not self.plugin_instance.allow_custom_url:
            return [field for field in fields if field != 'custom_url']
        return fields


admin.site.register(SaaS, SaaSAdmin)
