from django.contrib import admin
from django.conf.urls import url
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin, ChangePasswordAdminMixin
from orchestra.admin.actions import disable, enable
from orchestra.admin.utils import admin_link
from orchestra.contrib.accounts.actions import list_accounts
from orchestra.contrib.accounts.admin import SelectAccountAdminMixin
from orchestra.contrib.accounts.filters import IsActiveListFilter
from orchestra.forms import UserCreationForm, NonStoredUserChangeForm

from . import settings
from .filters import HasCustomAddressListFilter
from .models import List


class ListAdmin(ChangePasswordAdminMixin, SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'name', 'address_name', 'address_domain_link', 'account_link', 'display_active'
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('account_link', 'name', 'is_active')
        }),
        (_("Address"), {
            'classes': ('wide',),
            'fields': (('address_name', 'address_domain'),)
        }),
        (_("Admin"), {
            'classes': ('wide',),
            'fields': ('admin_email', 'password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('account_link', 'name', 'is_active')
        }),
        (_("Address"), {
            'classes': ('wide',),
            'description': _("Additional address besides the default &lt;name&gt;@%s"
                ) % settings.LISTS_DEFAULT_DOMAIN,
            'fields': (('address_name', 'address_domain'),)
        }),
        (_("Admin"), {
            'classes': ('wide',),
            'fields': ('password',),
        }),
    )
    search_fields = ('name', 'address_name', 'address_domain__name', 'account__username')
    list_filter = (IsActiveListFilter, HasCustomAddressListFilter)
    readonly_fields = ('account_link',)
    change_readonly_fields = ('name',)
    form = NonStoredUserChangeForm
    add_form = UserCreationForm
    list_select_related = ('account', 'address_domain',)
    filter_by_account_fields = ['address_domain']
    actions = (disable, enable, list_accounts)
    
    address_domain_link = admin_link('address_domain', order='address_domain__name')
    
    def get_urls(self):
        useradmin = UserAdmin(List, self.admin_site)
        return [
            url(r'^(\d+)/password/$',
                self.admin_site.admin_view(useradmin.user_change_password))
        ] + super(ListAdmin, self).get_urls()
    
    def save_model(self, request, obj, form, change):
        """ set password """
        if not change:
            obj.set_password(form.cleaned_data["password1"])
        super(ListAdmin, self).save_model(request, obj, form, change)


admin.site.register(List, ListAdmin)
