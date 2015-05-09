from django.contrib import admin
from django.conf.urls import patterns
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin, ChangePasswordAdminMixin
from orchestra.admin.actions import disable
from orchestra.admin.utils import admin_link
from orchestra.contrib.accounts.admin import SelectAccountAdminMixin
from orchestra.contrib.accounts.filters import IsActiveListFilter

from .forms import ListCreationForm, ListChangeForm
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
            'fields': (('address_name', 'address_domain'),)
        }),
        (_("Admin"), {
            'classes': ('wide',),
            'fields': ('password',),
        }),
    )
    search_fields = ('name', 'address_name', 'address_domain__name', 'account__username')
    list_filter = (IsActiveListFilter,)
    readonly_fields = ('account_link',)
    change_readonly_fields = ('name',)
    form = ListChangeForm
    add_form = ListCreationForm
    list_select_related = ('account', 'address_domain',)
    filter_by_account_fields = ['address_domain']
    actions = (disable,)
    
    address_domain_link = admin_link('address_domain', order='address_domain__name')
    
    def get_urls(self):
        useradmin = UserAdmin(List, self.admin_site)
        return patterns('',
            (r'^(\d+)/password/$',
             self.admin_site.admin_view(useradmin.user_change_password))
        ) + super(ListAdmin, self).get_urls()


admin.site.register(List, ListAdmin)
