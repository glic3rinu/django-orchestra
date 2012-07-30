from common.admin import AddOrChangeInlineFormMixin
from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from models import SystemUser, SystemGroup
from common.utils.admin import insert_inline, insert_list_filter, insert_list_display


def user_link(self):
    url = reverse('admin:auth_user_change', args=(self.pk,))
    return '<a href="%s">%s</a>' % (url, self.user)
user_link.short_description = _("User")
user_link.allow_tags = True
user_link.admin_order_field = 'user'


class SystemUserAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', user_link, 'uid', 'primary_group', 'shell', 'homedir', 'only_ftp']
    list_filter = ['only_ftp']


class SystemGroupAdmin(admin.ModelAdmin): 
    list_display = ['name', 'gid']


admin.site.register(SystemUser, SystemUserAdmin)
admin.site.register(SystemGroup, SystemGroupAdmin)


class ChangeSystemUserInlineForm(forms.ModelForm):
    class Meta:
        model = SystemUser


class AddSystemUserInlineForm(ChangeSystemUserInlineForm):
    enable = forms.BooleanField(label=_("Enable"))
    
    class Meta:
        fields = ('enable', 'primary_group', 'homedir')
        exclude = ('uid', 'shell')


#TODO: , ServiceAdminStackedInline
class SystemUserTabularInline(admin.TabularInline, AddOrChangeInlineFormMixin):
    model = SystemUser
    max_num = 0
    add_form = AddSystemUserInlineForm
    change_form = ChangeSystemUserInlineForm

insert_inline(User, SystemUserTabularInline)


class SystemUserFilter(SimpleListFilter):
    title = _('system user')
    parameter_name = 'system'

    def lookups(self, request, model_admin):
        return (
            ('Yes', _('Yes')),
            ('No', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.filter(systemuser__isnull=False)
        if self.value() == 'No':
            return queryset.filter(systemuser__isnull=True)

insert_list_filter(User, SystemUserFilter)


def system_user_status(self):
    return hasattr(self, 'systemuser')
system_user_status.short_description = _("System User")
system_user_status.boolean = True
system_user_status.admin_order_field = 'systemuser'

insert_list_display(User, system_user_status)
