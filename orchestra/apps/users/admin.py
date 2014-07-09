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
from .roles.filters import role_list_filter_factory


class UserAdmin(AccountAdminMixin, auth.UserAdmin, ExtendedModelAdmin):
    list_display = ('username', 'display_is_main')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {
            'fields': ('account', 'username', 'password')
        }),
        (_("Personal info"), {
            'fields': ('first_name', 'last_name', 'email')
        }),
        (_("Permissions"), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'display_is_main')
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
    search_fields = ['username', 'account__user__username']
    readonly_fields = ('display_is_main', 'account_link')
    change_readonly_fields = ('username',)
    filter_horizontal = ()
    add_form = UserCreationForm
    form = UserChangeForm
    roles = []
    ordering = ('-id',)
    
    def display_is_main(self, instance):
        return instance.is_main
    display_is_main.short_description = _("is main")
    display_is_main.boolean = True
    
    def get_urls(self):
        """ Returns the additional urls for the change view links """
        urls = super(UserAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        new_urls = patterns("")
        for role in self.roles:
            new_urls += patterns("",
                url('^(\d+)/%s/$' % role.url_name,
                    wrap_admin_view(self, role().change_view),
                    name='%s_%s_%s_change' % (opts.app_label, opts.model_name, role.name)),
                url('^(\d+)/%s/delete/$' % role.url_name,
                    wrap_admin_view(self, role().delete_view),
                    name='%s_%s_%s_delete' % (opts.app_label, opts.model_name, role.name))
            )
        return new_urls + urls
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super(UserAdmin, self).get_fieldsets(request, obj=obj)
        if obj and obj.account:
            fieldsets[0][1]['fields'] = ('account_link',) + fieldsets[0][1]['fields'][1:]
        return fieldsets
    
    def get_list_display(self, request):
        roles = []
        for role in self.roles:
            def has_role(user, role_class=role):
                role = role_class(user=user)
                if role.exists:
                    return '<img src="/static/admin/img/icon-yes.gif" alt="True">'
                url = reverse('admin:users_user_%s_change' % role.name, args=(user.pk,))
                false = '<img src="/static/admin/img/icon-no.gif" alt="False">'
                return '<a href="%s">%s</a>' % (url, false)
            has_role.short_description = _("Has %s") % role.name
            has_role.admin_order_field = role.name
            has_role.allow_tags = True
            roles.append(has_role)
        return list(self.list_display) + roles + ['account_link']
    
    def get_list_filter(self, request):
        roles = [ role_list_filter_factory(role) for role in self.roles ]
        return list(self.list_filter) + roles
    
    def change_view(self, request, object_id, **kwargs):
        user = self.get_object(User, unquote(object_id))
        extra_context = kwargs.get('extra_context', {})
        extra_context['roles'] = [ role(user=user) for role in self.roles ]
        kwargs['extra_context'] = extra_context
        return super(UserAdmin, self).change_view(request, object_id, **kwargs)
    
    def get_queryset(self, request):
        """ Select related for performance """
        related = ['account__user'] + [ role.name for role in self.roles ]
        return super(UserAdmin, self).get_queryset(request).select_related(*related)


admin.site.register(User, UserAdmin)
