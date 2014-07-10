from django.contrib import admin, messages
from django.contrib.contenttypes import generic
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.filters import UsedContentTypeFilter
from orchestra.admin.utils import insertattr, get_modeladmin
from orchestra.core import services
from orchestra.utils import running_syncdb

from .forms import ResourceForm
from .models import Resource, ResourceData, MonitorData


class ResourceAdmin(ExtendedModelAdmin):
    list_display = (
        'name', 'verbose_name', 'content_type', 'period', 'ondemand',
        'default_allocation', 'disable_trigger', 'crontab',
    )
    list_filter = (UsedContentTypeFilter, 'period', 'ondemand', 'disable_trigger')
    fieldsets = (
        (None, {
            'fields': ('name', 'content_type', 'period'),
        }),
        (_("Configuration"), {
            'fields': ('verbose_name', 'default_allocation', 'ondemand',
                       'disable_trigger', 'is_active'),
        }),
        (_("Monitoring"), {
            'fields': ('monitors', 'crontab'),
        }),
    )
    change_readonly_fields = ('name', 'content_type', 'period')
    
    def add_view(self, request, **kwargs):
        """ Warning user if the node is not fully configured """
        if request.method == 'GET':
            messages.warning(request, _(
                "Restarting orchestra and celery is required to fully apply changes. "
                "Remember that allocated values will be applied when objects are saved"
            ))
        return super(ResourceAdmin, self).add_view(request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        super(ResourceAdmin, self).save_model(request, obj, form, change)
        model = obj.content_type.model_class()
        modeladmin = get_modeladmin(model)
        resources = obj.content_type.resource_set.filter(is_active=True)
        inlines = []
        for inline in modeladmin.inlines:
            if inline.model is ResourceData:
                inline = resource_inline_factory(resources)
            inlines.append(inline)
        modeladmin.inlines = inlines
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ filter service content_types """
        if db_field.name == 'content_type':
            models = [ model._meta.model_name for model in services.get().keys() ]
            kwargs['queryset'] = db_field.rel.to.objects.filter(model__in=models)
        return super(ResourceAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class ResourceDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'resource', 'used', 'allocated', 'last_update',) # TODO content_object
    list_filter = ('resource',)


class MonitorDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'monitor', 'date', 'value') # TODO content_object
    list_filter = ('monitor',)


admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceData, ResourceDataAdmin)
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
        model = ResourceData
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

if not running_syncdb():
    # not run during syncdb
    for resources in Resource.group_by_content_type():
        inline = resource_inline_factory(resources)
        model = resources[0].content_type.model_class()
        insertattr(model, 'inlines', inline)
