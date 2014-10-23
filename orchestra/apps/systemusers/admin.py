from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.safestring import mark_safe

from orchestra.admin import ExtendedModelAdmin, ChangePasswordAdminMixin
from orchestra.admin.utils import wrap_admin_view
from orchestra.apps.accounts.admin import SelectAccountAdminMixin
from orchestra.forms import UserCreationForm, UserChangeForm

from .filters import IsMainListFilter
from .models import SystemUser


class SystemUserAdmin(ChangePasswordAdminMixin, SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = ('username', 'account_link', 'shell', 'home', 'display_active', 'display_main')
    list_filter = ('is_active', 'shell', IsMainListFilter)
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'account_link', 'is_active')
        }),
        (_("System"), {
            'fields': ('home', 'shell', 'groups'),
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('account_link', 'username', 'password1', 'password2')
        }),
        (_("System"), {
            'fields': ('home', 'shell', 'groups'),
        }),
    )
    search_fields = ['username']
    readonly_fields = ('account_link',)
    change_readonly_fields = ('username',)
    filter_horizontal = ('groups',)
    filter_by_account_fields = ('groups',)
    add_form = UserCreationForm
    form = UserChangeForm
    ordering = ('-id',)
    
    def display_active(self, user):
        return user.active
    display_active.short_description = _("Active")
    display_active.admin_order_field = 'is_active'
    display_active.boolean = True
    
    def display_main(self, user):
        return user.is_main
    display_main.short_description = _("Main")
    display_main.boolean = True
    
    def get_form(self, request, obj=None, **kwargs):
        """ exclude self reference on groups """
        form = super(SystemUserAdmin, self).get_form(request, obj=obj, **kwargs)
        if obj:
            # Has to be done here and not in the form because of strange phenomenon
            # derived from monkeypatching formfield.widget.render on AccountAdminMinxin,
            # don't ask.
            formfield = form.base_fields['groups']
            formfield.queryset = formfield.queryset.exclude(id=obj.id)
        return form
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_main:
            return False
        return super(SystemUserAdmin, self).has_delete_permission(request, obj=obj)

admin.site.register(SystemUser, SystemUserAdmin)
