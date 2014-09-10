from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.forms.models import BaseInlineFormSet

from .utils import set_url_query, action_to_view


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
        response = super(ChangeListDefaultFilter, self).changelist_view(request,
                extra_context=extra_context)
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
                    name='%s_%s_%s' % (opts.app_label,
                                       opts.model_name,
                                       action.url_name)))
        return new_urls + urls
    
    def get_change_view_actions(self):
        views = []
        for action in self.change_view_actions:
            if isinstance(action, basestring):
                action = getattr(self, action)
            view = action_to_view(action, self)
            view.url_name = getattr(action, 'url_name', action.__name__)
            view.verbose_name = getattr(action, 'verbose_name',
                    view.url_name.capitalize().replace('_', ' '))
            view.css_class = getattr(action, 'css_class', 'historylink')
            view.description = getattr(action, 'description', '')
            views.append(view)
        return views
    
    def change_view(self, request, object_id, **kwargs):
        if not 'extra_context' in kwargs:
            kwargs['extra_context'] = {}
        kwargs['extra_context']['object_tools_items'] = [
            action.__dict__ for action in self.get_change_view_actions()
        ]
        return super(ChangeViewActionsMixin, self).change_view(request, object_id, **kwargs)


class ChangeAddFieldsMixin(object):
    """ Enables to specify different set of fields for change and add views """
    add_fields = ()
    add_fieldsets = ()
    add_form = None
    change_readonly_fields = ()
    
    def get_readonly_fields(self, request, obj=None):
        fields = super(ChangeAddFieldsMixin, self).get_readonly_fields(request, obj=obj)
        if obj:
            return fields + self.change_readonly_fields
        return fields
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            if self.add_fieldsets:
                return self.add_fieldsets
            elif self.add_fields:
                return [(None, {'fields': self.add_fields})]
        return super(ChangeAddFieldsMixin, self).get_fieldsets(request, obj=obj)
    
    def get_inline_instances(self, request, obj=None):
        """ add_inlines and inline.parent_object """
        self.inlines = getattr(self, 'add_inlines', self.inlines)
        if obj:
            self.inlines = type(self).inlines
        inlines = super(ChangeAddFieldsMixin, self).get_inline_instances(request, obj=obj)
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
    pass
