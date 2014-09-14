from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.admin.util import unquote
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.six.moves.urllib.parse import parse_qsl
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import wrap_admin_view, admin_link, set_url_query
from orchestra.core import services, accounts

from .filters import HasMainUserListFilter
from .forms import AccountCreationForm, AccountChangeForm
from .models import Account


class AccountAdmin(ExtendedModelAdmin):
    list_display = ('name', 'user_link', 'type', 'is_active')
    list_filter = (
        'type', 'is_active', HasMainUserListFilter
    )
    add_fieldsets = (
        (_("User"), {
            'fields': ('username', 'password1', 'password2',),
        }),
        (_("Account info"), {
            'fields': (('type', 'language'), 'comments'),
        }),
    )
    fieldsets = (
        (_("User"), {
            'fields': ('user_link', 'password',),
        }),
        (_("Account info"), {
            'fields': (('type', 'language'), 'comments'),
        }),
    )
    readonly_fields = ('user_link',)
    search_fields = ('users__username',)
    add_form = AccountCreationForm
    form = AccountChangeForm
    change_form_template = 'admin/accounts/account/change_form.html'
    
    user_link = admin_link('user', order='user__username')
    
    def name(self, account):
        return account.name
    name.admin_order_field = 'user__username'
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'comments':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 4})
        return super(AccountAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method == 'GET':
            account = self.get_object(request, unquote(object_id))
            if not account.is_active:
                messages.warning(request, 'This account is disabled.')
        context = {
            'services': sorted(
                [ model._meta for model in services.get() if model is not Account ],
                key=lambda i: i.verbose_name_plural.lower()
            ),
            'accounts': sorted(
                [ model._meta for model in accounts.get() if model is not Account ],
                key=lambda i: i.verbose_name_plural.lower()
            )
        }
        context.update(extra_context or {})
        return super(AccountAdmin, self).change_view(request, object_id,
                form_url=form_url, extra_context=context)
    
    def save_model(self, request, obj, form, change):
        """ Save user and account, they are interdependent """
        if change:
            return super(AccountAdmin, self).save_model(request, obj, form, change)
        obj.user.save()
        obj.user_id = obj.user.pk
        obj.save()
        obj.user.account = obj
        obj.user.save()
    
    def get_queryset(self, request):
        """ Select related for performance """
        qs = super(AccountAdmin, self).get_queryset(request)
        related = ('user', 'invoicecontact')
        return qs.select_related(*related)


admin.site.register(Account, AccountAdmin)


class AccountListAdmin(AccountAdmin):
    """ Account list to allow account selection when creating new services """
    list_display = ('select_account', 'type', 'user')
    actions = None
    search_fields = ['user__username',]
    ordering = ('user__username',)
    
    def select_account(self, instance):
        # TODO get query string from request.META['QUERY_STRING'] to preserve filters
        context = {
            'url': '../?account=' + str(instance.pk),
            'name': instance.name
        }
        return '<a href="%(url)s">%(name)s</a>' % context
    select_account.short_description = _("account")
    select_account.allow_tags = True
    select_account.order_admin_field = 'user__username'
    
    def changelist_view(self, request, extra_context=None):
        opts = self.model._meta
        original_app_label = request.META['PATH_INFO'].split('/')[-5]
        original_model = request.META['PATH_INFO'].split('/')[-4]
        context = {
            'title': _("Select account for adding a new %s") % (original_model),
            'original_app_label': original_app_label,
            'original_model': original_model,
        }
        context.update(extra_context or {})
        return super(AccountListAdmin, self).changelist_view(request,
                extra_context=context)


class AccountAdminMixin(object):
    """ Provide basic account support to ModelAdmin and AdminInline classes """
    readonly_fields = ('account_link',)
    filter_by_account_fields = []
    change_list_template = 'admin/accounts/account/change_list.html'
    change_form_template = 'admin/accounts/account/change_form.html'
    
    def account_link(self, instance):
        account = instance.account if instance.pk else self.account
        url = reverse('admin:accounts_account_change', args=(account.pk,))
        pk = account.pk
        return '<a href="%s">%s</a>' % (url, str(account))
    account_link.short_description = _("account")
    account_link.allow_tags = True
    account_link.admin_order_field = 'account__user__username'
    
    def get_readonly_fields(self, request, obj=None):
        """ provide account for filter_by_account_fields """
        if obj:
            self.account = obj.account
        return super(AccountAdminMixin, self).get_readonly_fields(request, obj=obj)
    
    def get_queryset(self, request):
        """ Select related for performance """
        qs = super(AccountAdminMixin, self).get_queryset(request)
        return qs.select_related('account__user')
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Improve performance of account field and filter by account """
        if db_field.name == 'account':
            qs = kwargs.get('queryset', db_field.rel.to.objects)
            kwargs['queryset'] = qs.select_related('user')
        formfield = super(AccountAdminMixin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in self.filter_by_account_fields:
            if hasattr(self, 'account'):
                # Hack widget render in order to append ?account=id to the add url
                old_render = formfield.widget.render
                def render(*args, **kwargs):
                    output = old_render(*args, **kwargs)
                    output = output.replace('/add/"', '/add/?account=%s"' % self.account.pk)
                    return mark_safe(output)
                formfield.widget.render = render
                # Filter related object by account
                formfield.queryset = formfield.queryset.filter(account=self.account)
        return formfield
    
    def get_account_from_preserve_filters(self, request):
        preserved_filters = self.get_preserved_filters(request)
        preserved_filters = dict(parse_qsl(preserved_filters))
        cl_filters = preserved_filters.get('_changelist_filters')
        if cl_filters:
            return dict(parse_qsl(cl_filters)).get('account')
    
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        account_id = self.get_account_from_preserve_filters(request)
        verb = 'change' if object_id else 'add'
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
        return super(AccountAdminMixin, self).changeform_view(request,
                object_id=object_id, form_url=form_url, extra_context=context)
    
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
                        opts.verbose_name, account.name),
                })
            else:
                request_copy = request.GET.copy()
                request_copy.pop('account')
                request.GET = request_copy
        context.update(extra_context or {})
        return super(AccountAdminMixin, self).changelist_view(request,
                extra_context=context)


class SelectAccountAdminMixin(AccountAdminMixin):
    """ Provides support for accounts on ModelAdmin """
    def get_inline_instances(self, request, obj=None):
        inlines = super(AccountAdminMixin, self).get_inline_instances(request, obj=obj)
        if hasattr(self, 'account'):
            account = self.account
        else:
            account = Account.objects.get(pk=request.GET['account'])
        [ setattr(inline, 'account', account) for inline in inlines ]
        return inlines
    
    def get_urls(self):
        """ Hooks select account url """
        urls = super(AccountAdminMixin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        account_list = AccountListAdmin(Account, admin_site).changelist_view
        select_urls = patterns("",
            url("/select-account/$",
                wrap_admin_view(self, account_list),
                name='%s_%s_select_account' % info),
        )
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
                    'title': _("Add %s for %s") % (opts.verbose_name, self.account.name),
                    'from_account': bool(from_account_id),
                    'account': self.account,
                    'account_opts': Account._meta,
                }
                context.update(extra_context or {})
                return super(AccountAdminMixin, self).add_view(request,
                        form_url=form_url, extra_context=context)
        return HttpResponseRedirect('./select-account/?%s' % request.META['QUERY_STRING'])
    
    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        if not change:
            obj.account_id = self.account.pk
        obj.save()
