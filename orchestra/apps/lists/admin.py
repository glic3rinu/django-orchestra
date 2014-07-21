from django.contrib import admin
from django.conf.urls import patterns
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext, ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import admin_link
from orchestra.apps.accounts.admin import SelectAccountAdminMixin

from .forms import ListCreationForm, ListChangeForm
from .models import List


class ListAdmin(SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = ('name', 'address_name', 'address_domain_link', 'account_link')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('account_link', 'name',)
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
            'fields': ('account_link', 'name',)
        }),
        (_("Address"), {
            'classes': ('wide',),
            'fields': (('address_name', 'address_domain'),)
        }),
        (_("Admin"), {
            'classes': ('wide',),
            'fields': ('admin_email', 'password',),
        }),
    )
    readonly_fields = ('account_link',)
    change_readonly_fields = ('name',)
    form = ListChangeForm
    add_form = ListCreationForm
    filter_by_account_fields = ['address_domain']
    
    address_domain_link = admin_link('address_domain', order='address_domain__name')
    
    def get_urls(self):
        useradmin = UserAdmin(List, self.admin_site)
        return patterns('',
            (r'^(\d+)/password/$',
             self.admin_site.admin_view(useradmin.user_change_password))
        ) + super(ListAdmin, self).get_urls()


admin.site.register(List, ListAdmin)
