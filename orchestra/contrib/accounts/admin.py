import copy
import re
from urllib.parse import parse_qsl

from django import forms
from django.apps import apps
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.contrib.auth import admin as auth
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin, ChangePasswordAdminMixin
from orchestra.admin.actions import SendEmail
from orchestra.admin.utils import wrap_admin_view, admin_link, set_url_query
from orchestra.contrib.services.settings import SERVICES_IGNORE_ACCOUNT_TYPE
from orchestra.core import services, accounts
from orchestra.forms import UserChangeForm
from orchestra.utils.apps import isinstalled

from .actions import (list_contacts, service_report, delete_related_services, disable_selected,
    enable_selected)
from .forms import AccountCreationForm
from .models import Account


class AccountAdmin(ChangePasswordAdminMixin, auth.UserAdmin, ExtendedModelAdmin):
    list_display = ('username', 'full_name', 'type', 'is_active')
    list_filter = (
        'type', 'is_active',
    )
    add_fieldsets = (
        (_("User"), {
            'fields': ('username', 'password1', 'password2',),
        }),
        (_("Personal info"), {
            'fields': ('short_name', 'full_name', 'email', ('type', 'language'), 'comments'),
        }),
        (_("Permissions"), {
            'fields': ('is_superuser',)
        }),
    )
    fieldsets = (
        (_("User"), {
            'fields': ('username', 'password', 'main_systemuser_link')
        }),
        (_("Personal info"), {
            'fields': ('short_name', 'full_name', 'email', ('type', 'language'), 'comments'),
        }),
        (_("Permissions"), {
            'fields': ('is_superuser', 'is_active')
        }),
        (_("Important dates"), {
            'classes': ('collapse',),
            'fields': ('last_login', 'date_joined')
        }),
    )
    search_fields = ('username', 'short_name', 'full_name')
    add_form = AccountCreationForm
    form = UserChangeForm
    filter_horizontal = ()
    change_readonly_fields = ('username', 'main_systemuser_link', 'is_active')
    change_form_template = 'admin/accounts/account/change_form.html'
    actions = (
        disable_selected, enable_selected, delete_related_services, list_contacts, service_report,
        SendEmail()
    )
    change_view_actions = (disable_selected, service_report, enable_selected)
    ordering = ()
    
    main_systemuser_link = admin_link('main_systemuser')
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'comments':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 4})
        return super(AccountAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if not add:
            if request.method == 'GET' and not obj.is_active:
                messages.warning(request, 'This account is disabled.')
            context.update({
                'services': sorted(
                    [model._meta for model in services.get() if model is not Account],
                    key=lambda i: i.verbose_name_plural.lower()
                ),
                'accounts': sorted(
                    [model._meta for model in accounts.get() if model is not Account],
                    key=lambda i: i.verbose_name_plural.lower()
                )
            })
        return super(AccountAdmin, self).render_change_form(
            request, context, add, change, form_url, obj)
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super(AccountAdmin, self).get_fieldsets(request, obj)
        if not obj:
            fields = AccountCreationForm.create_related_fields
            if fields:
                fieldsets = copy.deepcopy(fieldsets)
                fieldsets = list(fieldsets)
                fieldsets.insert(1, (_("Related services"), {'fields': fields}))
        return fieldsets
    
    def save_model(self, request, obj, form, change):
        if not change:
            form.save_model(obj)
            form.save_related(obj)
        else:
            if isinstalled('orchestra.contrib.orders') and isinstalled('orchestra.contrib.services'):
                if 'type' in form.changed_data:
                    old_type = Account.objects.get(pk=obj.pk).type
                    new_type = form.cleaned_data['type']
                    context = {
                        'from': old_type.lower(),
                        'to': new_type.lower(),
                        'url': reverse('admin:orders_order_changelist'),
                    }
                    msg = ''
                    if old_type in SERVICES_IGNORE_ACCOUNT_TYPE and new_type not in SERVICES_IGNORE_ACCOUNT_TYPE:
                        context['url'] += '?account=%i&ignore=1' % obj.pk
                        msg = _("Account type has been changed from <i>%(from)s</i> to <i>%(to)s</i>. "
                                "You may want to mark <a href='%(url)s'>existing ignored orders</a> as not ignored.")
                    elif old_type not in SERVICES_IGNORE_ACCOUNT_TYPE and new_type in SERVICES_IGNORE_ACCOUNT_TYPE:
                        context['url'] += '?account=%i&ignore=0' % obj.pk
                        msg = _("Account type has been changed from <i>%(from)s</i> to <i>%(to)s</i>. "
                                "You may want to ignore <a href='%(url)s'>existing not ignored orders</a>.")
                    if msg:
                        messages.warning(request, mark_safe(msg % context))
            super(AccountAdmin, self).save_model(request, obj, form, change)
    
    def get_change_view_actions(self, obj=None):
        views = super().get_change_view_actions(obj=obj)
        if obj is not None:
            if obj.is_active:
                return [view for view in views if view.url_name != 'enable']
            return [view for view in views if view.url_name != 'disable']
        return views
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(Account, AccountAdmin)


class AccountListAdmin(AccountAdmin):
    """ Account list to allow account selection when creating new services """
    list_display = ('select_account', 'username', 'type', 'username')
    actions = None
    change_list_template = 'admin/accounts/account/select_account_list.html'
    
    def select_account(self, instance):
        # TODO get query string from request.META['QUERY_STRING'] to preserve filters
        context = {
            'url': '../?account=' + str(instance.pk),
            'name': instance.username,
            'plus': '<strong style="color:green; font-size:12px">+</strong>',
        }
        return _('<a href="%(url)s">%(plus)s Add to %(name)s</a>') % context
    select_account.short_description = _("account")
    select_account.allow_tags = True
    select_account.admin_order_field = 'username'
    
    def changelist_view(self, request, extra_context=None):
        app_label = request.META['PATH_INFO'].split('/')[-5]
        model = request.META['PATH_INFO'].split('/')[-4]
        model = apps.get_model(app_label, model)
        opts = model._meta
        context = {
            'title': _("Select account for adding a new %s") % (opts.verbose_name),
            'original_opts': opts,
        }
        context.update(extra_context or {})
        response = super(AccountListAdmin, self).changelist_view(request, extra_context=context)
        if hasattr(response, 'context_data'):
            # user has submitted a change list change, we redirect directly to the add view
            # if there is only one result
            query = request.GET.get('q', '')
            if query:
                try:
                    account = Account.objects.get(username=query)
                except Account.DoesNotExist:
                    pass
                else:
                    return HttpResponseRedirect('../?account=%i' % account.pk)
            queryset = response.context_data['cl'].queryset
            if len(queryset) == 1:
                return HttpResponseRedirect('../?account=%i' % queryset[0].pk)
        return response


class AccountAdminMixin(object):
    """ Provide basic account support to ModelAdmin and AdminInline classes """
    readonly_fields = ('account_link',)
    filter_by_account_fields = []
    change_list_template = 'admin/accounts/account/change_list.html'
    change_form_template = 'admin/accounts/account/change_form.html'
    account = None
    list_select_related = ('account',)
    
    def display_active(self, instance):
        if not instance.is_active:
            return '<img src="%s" alt="False">' % static('admin/img/icon-no.svg')
        elif not instance.account.is_active:
            msg = _("Account disabled")
            return '<img style="width:13px" src="%s" alt="False" title="%s">' % (static('admin/img/inline-delete.svg'), msg)
        return '<img src="%s" alt="False">' % static('admin/img/icon-yes.svg')
    display_active.short_description = _("active")
    display_active.allow_tags = True
    display_active.admin_order_field = 'is_active'
    
    def account_link(self, instance):
        account = instance.account if instance.pk else self.account
        return admin_link()(account)
    account_link.short_description = _("account")
    account_link.allow_tags = True
    account_link.admin_order_field = 'account__username'
    
    def get_form(self, request, obj=None, **kwargs):
        """ Warns user when object's account is disabled """
        form = super(AccountAdminMixin, self).get_form(request, obj, **kwargs)
        try:
            field = form.base_fields['is_active']
        except KeyError:
            pass
        else:
            opts = self.model._meta
            help_text = _(
                "Designates whether this %(name)s should be treated as active. "
                "Unselect this instead of deleting %(plural_name)s."
            ) % {
                'name': opts.verbose_name,
                'plural_name': opts.verbose_name_plural,
            }
            if obj and not obj.account.is_active:
                help_text += "<br><b style='color:red;'>This user's account is dissabled</b>"
            field.help_text = _(help_text)
        # Not available in POST
        form.initial_account = self.get_changeform_initial_data(request).get('account')
        return form
    
    def get_fields(self, request, obj=None):
        """ remove account or account_link depending on the case """
        fields = super(AccountAdminMixin, self).get_fields(request, obj)
        fields = list(fields)
        if obj is not None or getattr(self, 'account_id', None):
            try:
                fields.remove('account')
            except ValueError:
                pass
        else:
            try:
                fields.remove('account_link')
            except ValueError:
                pass
        return fields
    
    def get_readonly_fields(self, request, obj=None):
        """ provide account for filter_by_account_fields """
        if obj:
            self.account = obj.account
        return super(AccountAdminMixin, self).get_readonly_fields(request, obj)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Filter by account """
        formfield = super(AccountAdminMixin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in self.filter_by_account_fields:
            if self.account:
                # Hack widget render in order to append ?account=id to the add url
                old_render = formfield.widget.render
                
                def render(*args, **kwargs):
                    output = old_render(*args, **kwargs)
                    output = output.replace('/add/"', '/add/?account=%s"' % self.account.pk)
                    with_qargs = r'/add/?\1&account=%s"' % self.account.pk
                    output = re.sub(r'/add/\?([^".]*)"', with_qargs, output)
                    return mark_safe(output)
                
                formfield.widget.render = render
                # Filter related object by account
                formfield.queryset = formfield.queryset.filter(account=self.account)
                # Apply heuristic order by
                if not formfield.queryset.query.order_by:
                    related_fields = [f.name for f in db_field.related_model._meta.get_fields()]
                    if 'name' in related_fields:
                        formfield.queryset = formfield.queryset.order_by('name')
                    elif 'username' in related_fields:
                        formfield.queryset = formfield.queryset.order_by('username')
        elif db_field.name == 'account':
            if self.account:
                formfield.initial = self.account.pk
            elif Account.objects.count() == 1:
                formfield.initial = 1
            formfield.queryset = formfield.queryset.order_by('username')
        return formfield
    
    def get_formset(self, request, obj=None, **kwargs):
        """ provides form.account for convinience """
        formset = super(AccountAdminMixin, self).get_formset(request, obj, **kwargs)
        formset.form.account = self.account
        formset.account = self.account
        return formset
    
    def get_account_from_preserve_filters(self, request):
        preserved_filters = self.get_preserved_filters(request)
        preserved_filters = dict(parse_qsl(preserved_filters))
        cl_filters = preserved_filters.get('_changelist_filters')
        if cl_filters:
            return dict(parse_qsl(cl_filters)).get('account')
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        account_id = self.get_account_from_preserve_filters(request)
        if not object_id:
            if account_id:
                # Preselect account
                set_url_query(request, 'account', account_id)
        context = {
            'from_account': bool(account_id),
            'account': not account_id or Account.objects.get(pk=account_id),
            'account_opts': Account._meta,
        }
        context.update(extra_context or {})
        return super(AccountAdminMixin, self).changeform_view(
            request, object_id, form_url=form_url, extra_context=context)
    
    def changelist_view(self, request, extra_context=None):
        account_id = request.GET.get('account')
        context = {}
        if account_id:
            opts = self.model._meta
            account = Account.objects.get(pk=account_id)
            context = {
                'account': not account_id or Account.objects.get(pk=account_id),
                'account_opts': Account._meta,
                'all_selected': True,
            }
            if not request.GET.get('all'):
                context.update({
                    'all_selected': False,
                    'title': _("Select %s to change for %s") % (
                        opts.verbose_name, account.username),
                })
            else:
                request_copy = request.GET.copy()
                request_copy.pop('account')
                request.GET = request_copy
        context.update(extra_context or {})
        return super(AccountAdminMixin, self).changelist_view(request, extra_context=context)


class SelectAccountAdminMixin(AccountAdminMixin):
    """ Provides support for accounts on ModelAdmin """
    def get_inline_instances(self, request, obj=None):
        inlines = super(AccountAdminMixin, self).get_inline_instances(request, obj)
        if self.account:
            account = self.account
        else:
            account = Account.objects.get(pk=request.GET['account'])
        [setattr(inline, 'account', account) for inline in inlines]
        return inlines
    
    def get_urls(self):
        """ Hooks select account url """
        urls = super(AccountAdminMixin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        account_list = AccountListAdmin(Account, admin_site).changelist_view
        select_urls = [
            url("add/select-account/$",
                wrap_admin_view(self, account_list),
                name='%s_%s_select_account' % info),
        ]
        return select_urls + urls
    
    def add_view(self, request, form_url='', extra_context=None):
        """ Redirects to select account view if required """
        if request.user.is_superuser:
            from_account_id = self.get_account_from_preserve_filters(request)
            if from_account_id:
                set_url_query(request, 'account', from_account_id)
            account_id = request.GET.get('account')
            if account_id or Account.objects.count() == 1:
                kwargs = {}
                if account_id:
                    kwargs = dict(pk=account_id)
                self.account = Account.objects.get(**kwargs)
                opts = self.model._meta
                context = {
                    'title': _("Add %s for %s") % (opts.verbose_name, self.account.username),
                    'from_account': bool(from_account_id),
                    'from_select': True,
                    'account': self.account,
                    'account_opts': Account._meta,
                }
                context.update(extra_context or {})
                return super(AccountAdminMixin, self).add_view(
                    request, form_url=form_url, extra_context=context)
        return HttpResponseRedirect('./select-account/?%s' % request.META['QUERY_STRING'])
    
    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        if not change:
            obj.account_id = self.account.pk
        obj.save()
