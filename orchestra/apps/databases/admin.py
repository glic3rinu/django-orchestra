from django.conf.urls import patterns
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import admin_link
from orchestra.apps.accounts.admin import AccountAdminMixin, SelectAccountAdminMixin

from .forms import (DatabaseUserChangeForm, DatabaseUserCreationForm,
        DatabaseCreationForm)
from .models import Database, Role, DatabaseUser


class UserInline(admin.TabularInline):
    model = Role
    verbose_name_plural = _("Users")
    readonly_fields = ('user_link',)
    extra = 0
    
    user_link = admin_link('user')
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'user':
            users = db_field.rel.to.objects.filter(type=self.parent_object.type)
            kwargs['queryset'] = users.filter(account=self.account)
        return super(UserInline, self).formfield_for_dbfield(db_field, **kwargs)


class PermissionInline(AccountAdminMixin, admin.TabularInline):
    model = Role
    verbose_name_plural = _("Permissions")
    readonly_fields = ('database_link',)
    extra = 0
    filter_by_account_fields = ['database']
    
    database_link = admin_link('database', popup=True)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        formfield = super(PermissionInline, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'database':
            # Hack widget render in order to append ?account=id to the add url
            db_type = self.parent_object.type
            old_render = formfield.widget.render
            def render(*args, **kwargs):
                output = old_render(*args, **kwargs)
                output = output.replace('/add/?', '/add/?type=%s&' % db_type)
                return mark_safe(output)
            formfield.widget.render = render
            formfield.queryset = formfield.queryset.filter(type=db_type)
        return formfield


class DatabaseAdmin(SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = ('name', 'type', 'account_link')
    list_filter = ('type',)
    search_fields = ['name']
    inlines = [UserInline]
    add_inlines = []
    change_readonly_fields = ('name', 'type')
    extra = 1
    fieldsets = (
        (None, {
            'classes': ('extrapretty',),
            'fields': ('account_link', 'name', 'type'),
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
                user = DatabaseUser.objects.create(
                    username=form.cleaned_data['username'],
                    type=obj.type,
                    account_id = obj.account.pk,
                )
                user.set_password(form.cleaned_data["password1"])
            user.save()
            Role.objects.create(database=obj, user=user, is_owner=True)


class DatabaseUserAdmin(SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = ('username', 'type', 'account_link')
    list_filter = ('type',)
    search_fields = ['username']
    form = DatabaseUserChangeForm
    add_form = DatabaseUserCreationForm
    change_readonly_fields = ('username', 'type')
    inlines = [PermissionInline]
    add_inlines = []
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
