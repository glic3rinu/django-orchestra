import sys

from django.contrib import admin
from django.contrib.contenttypes import generic
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.filters import UsedContentTypeFilter
from orchestra.admin.utils import insertattr, get_modeladmin

from .forms import ResourceForm
from .models import Resource, ResourceAllocation, Monitor, MonitorData


class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'verbose_name', 'content_type', 'period', 'ondemand',
        'default_allocation', 'disable_trigger'
    )
    list_filter = (UsedContentTypeFilter, 'period', 'ondemand', 'disable_trigger')

    def save_model(self, request, obj, form, change):
        super(ResourceAdmin, self).save_model(request, obj, form, change)
        model = obj.content_type.model_class()
        modeladmin = get_modeladmin(model)
        resources = obj.content_type.resource_set.filter(is_active=True)
        inlines = []
        for inline in modeladmin.inlines:
            if inline.model is ResourceAllocation:
                inline = resource_inline_factory(resources)
            inlines.append(inline)
        modeladmin.inlines = inlines


class ResourceAllocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'resource', 'content_object', 'value')
    list_filter = ('resource',)


class MonitorAdmin(admin.ModelAdmin):
    list_display = ('backend', 'resource', 'crontab')
    list_filter = ('backend', 'resource')


class MonitorDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'monitor', 'content_object', 'date', 'value')
    list_filter = ('monitor',)


admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceAllocation, ResourceAllocationAdmin)
admin.site.register(Monitor, MonitorAdmin)
admin.site.register(MonitorData, MonitorDataAdmin)


# Mokey-patching

def resource_inline_factory(resources):
    class ResourceInlineFormSet(generic.BaseGenericInlineFormSet):
        def total_form_count(self):
            return len(resources)
        
        @cached_property
        def forms(self):
            forms = []
            for i, resource in enumerate(resources):
                forms.append(self._construct_form(i, resource=resource))
            return forms
    
    class ResourceInline(generic.GenericTabularInline):
        model = ResourceAllocation
        verbose_name_plural = _("resources")
        form = ResourceForm
        formset = ResourceInlineFormSet
        
        class Media:
            css = {
                'all': ('orchestra/css/hide-inline-id.css',)
            }
        
        def has_add_permission(self, *args, **kwargs):
            """ Hidde add another """
            return False
    
    return ResourceInline

if not 'migrate' in sys.argv and not 'syncdb' in sys.argv:
    # not run during syncdb
    for resources in Resource.group_by_content_type():
        inline = resource_inline_factory(resources)
        model = resources[0].content_type.model_class()
        insertattr(model, 'inlines', inline)
