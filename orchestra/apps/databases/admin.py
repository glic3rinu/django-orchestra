from django.conf.urls import patterns
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin, ChangePasswordAdminMixin
from orchestra.admin.utils import admin_link
from orchestra.apps.accounts.admin import AccountAdminMixin, SelectAccountAdminMixin

from .forms import DatabaseCreationForm, DatabaseUserChangeForm, DatabaseUserCreationForm
from .models import Database, DatabaseUser


class DatabaseAdmin(SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = ('name', 'type', 'account_link')
    list_filter = ('type',)
    search_fields = ['name']
    change_readonly_fields = ('name', 'type')
    extra = 1
    fieldsets = (
        (None, {
            'classes': ('extrapretty',),
            'fields': ('account_link', 'name', 'type', 'users'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('account_link', 'name', 'type')
        }),
        (_("Create new user"), {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_("Use existing user"), {
            'classes': ('wide',),
            'fields': ('user',)
        }),
    )
    add_form = DatabaseCreationForm
    
    def save_model(self, request, obj, form, change):
        super(DatabaseAdmin, self).save_model(request, obj, form, change)
        if not change:
            user = form.cleaned_data['user']
            if not user:
                user = DatabaseUser(
                    username=form.cleaned_data['username'],
                    type=obj.type,
                    account_id=obj.account.pk,
                )
                user.set_password(form.cleaned_data["password1"])
            user.save()
            obj.users.add(user)


class DatabaseUserAdmin(SelectAccountAdminMixin, ChangePasswordAdminMixin, ExtendedModelAdmin):
    list_display = ('username', 'type', 'account_link')
    list_filter = ('type',)
    search_fields = ['username']
    form = DatabaseUserChangeForm
    add_form = DatabaseUserCreationForm
    change_readonly_fields = ('username', 'type')
    fieldsets = (
        (None, {
            'classes': ('extrapretty',),
            'fields': ('account_link', 'username', 'password', 'type')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('extrapretty',),
            'fields': ('account_link', 'username', 'password1', 'password2', 'type')
        }),
    )
    
    def get_urls(self):
        useradmin = UserAdmin(DatabaseUser, self.admin_site)
        return patterns('',
            (r'^(\d+)/password/$',
             self.admin_site.admin_view(useradmin.user_change_password))
        ) + super(DatabaseUserAdmin, self).get_urls()


admin.site.register(Database, DatabaseAdmin)
admin.site.register(DatabaseUser, DatabaseUserAdmin)
