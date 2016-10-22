from urllib import parse

from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.admin.utils import unquote
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.forms.models import BaseInlineFormSet
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters

from orchestra.models.utils import has_db_field

from ..utils.python import random_ascii, pairwise

from .forms import AdminPasswordChangeForm
#, AdminRawPasswordChangeForm
#from django.contrib.auth.forms import AdminPasswordChangeForm
from .utils import action_to_view


sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class ChangeListDefaultFilter(object):
    """
    Enables support for default filtering on admin change list pages
    Your model admin class should define an default_changelist_filters attribute
    default_changelist_filters = (('my_nodes', 'True'),)
    """
    default_changelist_filters = ()
    
    def changelist_view(self, request, extra_context=None):
#        defaults = []
#        for key, value in self.default_changelist_filters:
#            set_url_query(request, key, value)
#            defaults.append(key)
#        # hack response cl context in order to hook default filter awaearness
#        # into search_form.html template
#        response = super(ChangeListDefaultFilter, self).changelist_view(request, extra_context)
#        if hasattr(response, 'context_data') and 'cl' in response.context_data:
#            response.context_data['cl'].default_changelist_filters = defaults
#        return response
        querystring = request.META['QUERY_STRING']
        querydict = parse.parse_qs(querystring)
        redirect = False
        for field, value in self.default_changelist_filters:
            if field not in querydict:
                redirect = True
                querydict[field] = value
        if redirect:
            querystring = parse.urlencode(querydict, doseq=True)
            return HttpResponseRedirect(request.path + '?%s' % querystring)
        return super(ChangeListDefaultFilter, self).changelist_view(request, extra_context=extra_context)


class AtLeastOneRequiredInlineFormSet(BaseInlineFormSet):
    def clean(self):
        """Check that at least one service has been entered."""
        super(AtLeastOneRequiredInlineFormSet, self).clean()
        if any(self.errors):
            return
        if not any(cleaned_data and not cleaned_data.get('DELETE', False)
            for cleaned_data in self.cleaned_data):
            raise forms.ValidationError('At least one item required.')


class EnhaceSearchMixin(object):
    def lookup_allowed(self, lookup, value):
        """ allows any lookup """
        if 'password' in lookup:
            return False
        return True
    
    def get_search_results(self, request, queryset, search_term):
        """ allows to specify field <field_name>:<search_term> """
        search_fields = self.get_search_fields(request)
        if '=' in search_term:
            fields = {field.split('__')[0]: field for field in search_fields}
            new_search_term = []
            for part in search_term.split():
                field = None
                if '=' in part:
                    field, term = part.split('=')
                    kwarg = '%s__icontains'
                    c_term = term
                    if term.startswith(('"', "'")) and term.endswith(('"', "'")):
                        c_term = term[1:-1]
                        kwarg = '%s__iexact'
                    if field in fields:
                        queryset = queryset.filter(**{kwarg % fields[field]: c_term})
                    else:
                        new_search_term.append('='.join((field, term)))
                else:
                    new_search_term.append(part)
            search_term = ' '.join(new_search_term)
        return super(EnhaceSearchMixin, self).get_search_results(request, queryset, search_term)


class ChangeViewActionsMixin(object):
    """ Makes actions visible on the admin change view page. """
    change_view_actions = ()
    change_form_template = 'orchestra/admin/change_form.html'
    
    def get_urls(self):
        """Returns the additional urls for the change view links"""
        urls = super(ChangeViewActionsMixin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        new_urls = []
        for action in self.get_change_view_actions():
            new_urls.append(
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
            if isinstance(action, str):
                action = getattr(self, action)
            view = action_to_view(action, self)
            view.url_name = getattr(action, 'url_name', action.__name__)
            tool_description = getattr(action, 'tool_description', '')
            if not tool_description:
                tool_description = getattr(action, 'short_description',
                        view.url_name.capitalize().replace('_', ' '))
            if hasattr(tool_description, '__call__'):
                tool_description = tool_description(obj)
            view.tool_description = tool_description
            view.css_class = getattr(action, 'css_class', 'historylink')
            view.help_text = getattr(action, 'help_text', '')
            view.hidden = getattr(action, 'hidden', False)
            views.append(view)
        return views
    
    def change_view(self, request, object_id, **kwargs):
        if kwargs.get('extra_context', None) is None:
            kwargs['extra_context'] = {}
        obj = self.get_object(request, unquote(object_id))
        kwargs['extra_context']['object_tools_items'] = [
            action.__dict__ for action in self.get_change_view_actions(obj) if not action.hidden
        ]
        return super().change_view(request, object_id, **kwargs)


class ChangeAddFieldsMixin(object):
    """ Enables to specify different set of fields for change and add views """
    add_fields = ()
    add_fieldsets = ()
    add_form = None
    add_prepopulated_fields = {}
    change_readonly_fields = ()
    change_form = None
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
        if obj is None:
            if self.add_form:
                defaults['form'] = self.add_form
        else:
            if self.change_form:
                defaults['form'] = self.change_form
        defaults.update(kwargs)
        return super(ChangeAddFieldsMixin, self).get_form(request, obj, **defaults)


class ExtendedModelAdmin(ChangeViewActionsMixin,
                         ChangeAddFieldsMixin,
                         ChangeListDefaultFilter,
                         EnhaceSearchMixin,
                         admin.ModelAdmin):
    list_prefetch_related = None
    
    def get_queryset(self, request):
        qs = super(ExtendedModelAdmin, self).get_queryset(request)
        if self.list_prefetch_related:
            qs = qs.prefetch_related(*self.list_prefetch_related)
        return qs
    
    def get_object(self, request, object_id, from_field=None):
        obj = super(ExtendedModelAdmin, self).get_object(request, object_id, from_field)
        if obj is None:
            opts = self.model._meta
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {
                'name': force_text(opts.verbose_name), 'key': escape(object_id)})
        return obj


class ChangePasswordAdminMixin(object):
    change_password_form = AdminPasswordChangeForm
    change_user_password_template = 'admin/orchestra/change_password.html'
    
    def get_urls(self):
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        return [
            url(r'^(\d+)/password/$',
                self.admin_site.admin_view(self.change_password),
                name='%s_%s_change_password' % info),
            url(r'^(\d+)/hash/$',
                self.admin_site.admin_view(self.show_hash),
                name='%s_%s_show_hash' % info)
        ] + super().get_urls()
    
    def get_change_password_username(self, obj):
        return str(obj)
    
    @sensitive_post_parameters_m
    def change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        # TODO use this insetad of self.get_object(), in other places
        obj = get_object_or_404(self.get_queryset(request), pk=id)
        raw = request.GET.get('raw', '0') == '1'
        can_raw = has_db_field(obj, 'password')
        if raw and not can_raw:
            raise TypeError("%s has no password db field for raw password edditing." % obj)
        related = []
        for obj_name_attr in ('username', 'name', 'hostname'):
            try:
                obj_name = getattr(obj, obj_name_attr)
            except AttributeError:
                pass
            else:
                break
        if hasattr(obj, 'account'):
            account = obj.account
            if obj.account.username == obj_name:
                related.append(obj.account)
        else:
            account = obj
        if account.username == obj_name:
            for rel in account.get_related_passwords(db_field=raw):
                if not isinstance(obj, type(rel)):
                    related.append(rel)
        
        if request.method == 'POST':
            form = self.change_password_form(obj, request.POST, related=related, raw=raw)
            if form.is_valid():
                form.save()
                self.log_change(request, obj, _("Password changed."))
                msg = _('Password changed successfully.')
                messages.success(request, msg)
                update_session_auth_hash(request, form.user) # This is safe
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(obj, related=related, raw=raw)
        
        fieldsets = [
            (obj._meta.verbose_name.capitalize(), {
                'classes': ('wide',),
                'fields': ('password',) if raw else ('password1', 'password2'),
            }),
        ]
        for ix, rel in enumerate(related):
            fieldsets.append((rel._meta.verbose_name.capitalize(), {
                'classes': ('wide',),
                'fields': ('password_%i' % ix,) if raw else ('password1_%i' % ix, 'password2_%i' % ix)
            }))
        
        obj_username = self.get_change_password_username(obj)
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})
        context = {
            'title': _('Change password: %s') % obj_username,
            'adminform': adminForm,
            'raw': raw,
            'can_raw': can_raw,
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
            'original': obj,
            'obj_username': obj_username,
            'save_as': False,
            'show_save': True,
            'password': random_ascii(10),
        }
        context.update(admin.site.each_context(request))
        return TemplateResponse(request, self.change_user_password_template, context)
    
    def show_hash(self, request, id):
        if not request.user.is_superuser:
            raise PermissionDenied
        obj = get_object_or_404(self.get_queryset(request), pk=id)
        return HttpResponse(obj.password)
