from django.conf.urls import patterns
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.apps.accounts.admin import AccountAdminMixin

from .forms import VPSChangeForm, VPSCreationForm
from .models import VPS


class VPSAdmin(AccountAdminMixin, ExtendedModelAdmin):
    list_display = ('hostname', 'type', 'template', 'account_link')
    list_filter = ('type', 'template')
    form = VPSChangeForm
    add_form = VPSCreationForm
    readonly_fields = ('account_link',)
    change_readonly_fields = ('account', 'name', 'type', 'template')
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('account_link', 'hostname', 'type', 'template')
        }),
        (_("Login"), {
            'classes': ('wide',),
            'fields': ('password',)
        })
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('account', 'hostname', 'type', 'template')
        }),
        (_("Login"), {
            'classes': ('wide',),
            'fields': ('password1', 'password2',)
        }),
    )
    
    def get_urls(self):
        useradmin = UserAdmin(VPS, self.admin_site)
        return patterns('',
            (r'^(\d+)/password/$',
             self.admin_site.admin_view(useradmin.user_change_password))
        ) + super(VPSAdmin, self).get_urls()


admin.site.register(VPS, VPSAdmin)
