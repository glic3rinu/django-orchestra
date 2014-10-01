from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.utils.translation import ugettext, ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import wrap_admin_view
from orchestra.apps.accounts.admin import SelectAccountAdminMixin

from .forms import UserCreationForm, UserChangeForm
from .models import SystemUser


class SystemUserAdmin(SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = ('username', 'account_link', 'shell', 'home', 'is_active',)
    list_filter = ('is_active', 'shell')
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
            'fields': ('username', 'password1', 'password2', 'account')
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


admin.site.register(SystemUser, SystemUserAdmin)
