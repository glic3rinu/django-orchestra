from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.contrib.auth import admin as auth
from django.utils.translation import ugettext, ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import wrap_admin_view
from orchestra.apps.accounts.admin import AccountAdminMixin

from .forms import UserCreationForm, UserChangeForm
from .models import User


class UserAdmin(AccountAdminMixin, auth.UserAdmin, ExtendedModelAdmin):
    list_display = ('username', 'account_link', 'is_main', 'is_superuser', 'is_active')
    list_filter = ('is_main', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'account_link')
        }),
        (_("System"), {
            'fields': ('home', 'shell', 'groups'),
        }),
        (_("Personal info"), {
            'fields': ('first_name', 'last_name', 'email')
        }),
        (_("Permissions"), {
            'fields': ('is_main', 'is_active', 'is_superuser')
        }),
        (_("Important dates"), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'account'),
        }),
    )
    search_fields = ['username']
    readonly_fields = ('is_main', 'account_link',)
    change_readonly_fields = ('username',)
    filter_horizontal = ()
    filter_by_account_fields = ('groups',)
    add_form = UserCreationForm
    form = UserChangeForm
    ordering = ('-id',)
    
    def get_form(self, request, obj=None, **kwargs):
        """ exclude self reference on groups """
        form = super(AccountAdminMixin, self).get_form(request, obj=obj, **kwargs)
        if obj:
            # Has to be done here and not in the form because of strange phenomenon
            # derived from monkeypatching formfield.widget.render on AccountAdminMinxin,
            # don't ask.
            formfield = form.base_fields['groups']
            formfield.queryset = formfield.queryset.exclude(id=obj.id)
        return form


admin.site.register(User, UserAdmin)
