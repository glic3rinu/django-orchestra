from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .utils import set_url_query


class ExtendedModelAdmin(admin.ModelAdmin):
    add_fields = ()
    add_fieldsets = ()
    add_form = None
    change_readonly_fields = ()
    
    def get_readonly_fields(self, request, obj=None):
        fields = super(ExtendedModelAdmin, self).get_readonly_fields(request, obj=obj)
        if obj:
            return fields + self.change_readonly_fields
        return fields
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            if self.add_fieldsets:
                return self.add_fieldsets
            elif self.add_fields:
                return [(None, {'fields': self.add_fields})]
        return super(ExtendedModelAdmin, self).get_fieldsets(request, obj=obj)
    
    def get_inline_instances(self, request, obj=None):
        """ add_inlines and inline.parent_object """
        self.inlines = getattr(self, 'add_inlines', self.inlines)
        if obj:
            self.inlines = type(self).inlines
        inlines = super(ExtendedModelAdmin, self).get_inline_instances(request, obj=obj)
        for inline in inlines:
            inline.parent_object = obj
        return inlines
    
    def get_form(self, request, obj=None, **kwargs):
        """ Use special form during user creation """
        defaults = {}
        if obj is None and self.add_form:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super(ExtendedModelAdmin, self).get_form(request, obj, **defaults)


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
        # hack response cl context in order to hook default filter awaearness into search_form.html template
        response = super(ChangeListDefaultFilter, self).changelist_view(request, extra_context=extra_context)
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
