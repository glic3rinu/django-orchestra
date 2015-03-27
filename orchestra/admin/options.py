from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.forms.models import BaseInlineFormSet
from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.text import camel_case_to_spaces
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters

from .forms import AdminPasswordChangeForm
#from django.contrib.auth.forms import AdminPasswordChangeForm
from .utils import set_url_query, action_to_view, wrap_admin_view


sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class ChangeListDefaultFilter(object):
    """
    Enables support for default filtering on admin change list pages
    Your model admin class should define an default_changelist_filters attribute
    default_changelist_filters = (('my_nodes', 'True'),)
    """
    default_changelist_filters = ()
    
    def changelist_view(self, request, extra_context=None):
        """ Default filter as 'my_nodes=True' """
        defaults = []
        for key, value in self.default_changelist_filters:
             set_url_query(request, key, value)
             defaults.append(key)
        # hack response cl context in order to hook default filter awaearness
        # into search_form.html template
        response = super(ChangeListDefaultFilter, self).changelist_view(request, extra_context)
        if hasattr(response, 'context_data') and 'cl' in response.context_data:
            response.context_data['cl'].default_changelist_filters = defaults
        return response


class AtLeastOneRequiredInlineFormSet(BaseInlineFormSet):
    def clean(self):
        """Check that at least one service has been entered."""
        super(AtLeastOneRequiredInlineFormSet, self).clean()
        if any(self.errors):
            return
        if not any(cleaned_data and not cleaned_data.get('DELETE', False)
            for cleaned_data in self.cleaned_data):
            raise forms.ValidationError('At least one item required.')


class ChangeViewActionsMixin(object):
    """ Makes actions visible on the admin change view page. """
    change_view_actions = ()
    change_form_template = 'orchestra/admin/change_form.html'
    
    def get_urls(self):
        """Returns the additional urls for the change view links"""
        urls = super(ChangeViewActionsMixin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        new_urls = patterns('')
        for action in self.get_change_view_actions():
            new_urls += patterns('',
                url('^(\d+)/%s/$' % action.url_name,
                    admin_site.admin_view(action),
                    name='%s_%s_%s' % (opts.app_label, opts.model_name, action.url_name)
                )
            )
        return new_urls + urls
    
    def get_change_view_actions(self, obj=None):
        """ allow customization on modelamdin """
        views = []
        for action in self.change_view_actions:
            if isinstance(action, basestring):
                action = getattr(self, action)
            view = action_to_view(action, self)
            view.url_name = getattr(action, 'url_name', action.__name__)
            verbose_name = getattr(action, 'verbose_name',
                    view.url_name.capitalize().replace('_', ' '))
            if hasattr(verbose_name, '__call__'):
                verbose_name = verbose_name(obj)
            view.verbose_name = verbose_name
            view.css_class = getattr(action, 'css_class', 'historylink')
            view.description = getattr(action, 'description', '')
            views.append(view)
        return views
    
    def change_view(self, request, object_id, **kwargs):
        if kwargs.get('extra_context', None) is None:
            kwargs['extra_context'] = {}
        obj = self.get_object(request, unquote(object_id))
        kwargs['extra_context']['object_tools_items'] = [
            action.__dict__ for action in self.get_change_view_actions(obj)
        ]
        return super(ChangeViewActionsMixin, self).change_view(request, object_id, **kwargs)


class ChangeAddFieldsMixin(object):
    """ Enables to specify different set of fields for change and add views """
    add_fields = ()
    add_fieldsets = ()
    add_form = None
    add_prepopulated_fields = {}
    change_readonly_fields = ()
    add_inlines = None
    
    def get_prepopulated_fields(self, request, obj=None):
        if not obj:
            return super(ChangeAddFieldsMixin, self).get_prepopulated_fields(request, obj)
        return {}
    
    def get_change_readonly_fields(self, request, obj=None):
        return self.change_readonly_fields
    
    def get_readonly_fields(self, request, obj=None):
        fields = super(ChangeAddFieldsMixin, self).get_readonly_fields(request, obj)
        if obj:
            return fields + self.get_change_readonly_fields(request, obj)
        return fields
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            if self.add_fieldsets:
                return self.add_fieldsets
            elif self.add_fields:
                return [(None, {'fields': self.add_fields})]
        return super(ChangeAddFieldsMixin, self).get_fieldsets(request, obj)
    
    def get_inline_instances(self, request, obj=None):
        """ add_inlines and inline.parent_object """
        if obj:
            self.inlines = type(self).inlines
        else:
            self.inlines = self.inlines if self.add_inlines is None else self.add_inlines
        inlines = super(ChangeAddFieldsMixin, self).get_inline_instances(request, obj)
        for inline in inlines:
            inline.parent_object = obj
        return inlines
    
    def get_form(self, request, obj=None, **kwargs):
        """ Use special form during user creation """
        defaults = {}
        if obj is None and self.add_form:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super(ChangeAddFieldsMixin, self).get_form(request, obj, **defaults)


class ExtendedModelAdmin(ChangeViewActionsMixin, ChangeAddFieldsMixin, admin.ModelAdmin):
    list_prefetch_related = None
    
    def get_queryset(self, request):
        qs = super(ExtendedModelAdmin, self).get_queryset(request)
        if self.list_prefetch_related:
            qs = qs.prefetch_related(*self.list_prefetch_related)
        return qs


class ChangePasswordAdminMixin(object):
    change_password_form = AdminPasswordChangeForm
    change_user_password_template = 'admin/orchestra/change_password.html'
    
    def get_urls(self):
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        return patterns('',
            url(r'^(\d+)/password/$',
                self.admin_site.admin_view(self.change_password),
                name='%s_%s_change_password' % info),
        ) + super(ChangePasswordAdminMixin, self).get_urls()
    
    @sensitive_post_parameters_m
    def change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        # TODO use this insetad of self.get_object(), in other places
        user = get_object_or_404(self.get_queryset(request), pk=id)
        
        related = []
        try:
            # don't know why getattr(user, 'username', user.name) doesn't work
            username = user.username
        except AttributeError:
            username = user.name
        if hasattr(user, 'account'):
            account = user.account
            if user.account.username == username:
                related.append(user.account)
        else:
            account = user
        if account.username == username:
            for rel in account.get_related_passwords():
                if not isinstance(user, type(rel)):
                    related.append(rel)
        
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST, related=related)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, user, change_message)
                msg = _('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user) # This is safe
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user, related=related)
        
        fieldsets = [
            (user._meta.verbose_name.capitalize(), {
                'classes': ('wide',),
                'fields': ('password1', 'password2')
            }),
        ]
        for ix, rel in enumerate(related):
            fieldsets.append((rel._meta.verbose_name.capitalize(), {
                'classes': ('wide',),
                'fields': ('password1_%i' % ix, 'password2_%i' % ix)
            }))
        
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})
        context = {
            'title': _('Change password: %s') % escape(username),
            'adminform': adminForm,
            'errors': admin.helpers.AdminErrorList(form, []),
            'form_url': form_url,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        context.update(admin.site.each_context())
        return TemplateResponse(request,
            self.change_user_password_template,
            context, current_app=self.admin_site.name)
