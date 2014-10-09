from django.contrib import admin, messages
from django.contrib.contenttypes import generic
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.filters import UsedContentTypeFilter
from orchestra.admin.utils import insertattr, get_modeladmin, admin_link, admin_date
from orchestra.core import services
from orchestra.utils import database_ready

from .forms import ResourceForm
from .models import Resource, ResourceData, MonitorData


class ResourceAdmin(ExtendedModelAdmin):
    list_display = (
        'id', 'verbose_name', 'content_type', 'period', 'on_demand',
        'default_allocation', 'unit', 'disable_trigger', 'crontab',
    )
    list_filter = (UsedContentTypeFilter, 'period', 'on_demand', 'disable_trigger')
    fieldsets = (
        (None, {
            'fields': ('name', 'content_type', 'period'),
        }),
        (_("Configuration"), {
            'fields': ('verbose_name', 'unit', 'scale', 'on_demand',
                       'default_allocation', 'disable_trigger', 'is_active'),
        }),
        (_("Monitoring"), {
            'fields': ('monitors', 'crontab'),
        }),
    )
    change_readonly_fields = ('name', 'content_type', 'period')
    
    def add_view(self, request, **kwargs):
        """ Warning user if the node is not fully configured """
        if request.method == 'POST':
            messages.warning(request, _(
                "Restarting orchestra and celerybeat is required to fully apply changes. "
                "Remember that new allocated values will be applied when objects are saved."
            ))
        return super(ResourceAdmin, self).add_view(request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        super(ResourceAdmin, self).save_model(request, obj, form, change)
        model = obj.content_type.model_class()
        modeladmin = type(get_modeladmin(model))
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
            models = [ model._meta.model_name for model in services.get() ]
            kwargs['queryset'] = db_field.rel.to.objects.filter(model__in=models)
        return super(ResourceAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class ResourceDataAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'resource_link', 'used', 'allocated', 'updated_at', 'content_object_link'
    )
    list_filter = ('resource',)
    readonly_fields = ('content_object_link',)
    
    resource_link = admin_link('resource')
    content_object_link = admin_link('content_object')
    
    def get_queryset(self, request):
        queryset = super(ResourceDataAdmin, self).get_queryset(request)
        return queryset.prefetch_related('content_object')


class MonitorDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'monitor', 'created_at', 'value', 'content_object_link')
    list_filter = ('monitor',)
    readonly_fields = ('content_object_link',)
    
    content_object_link = admin_link('content_object')
    
    def get_queryset(self, request):
        queryset = super(MonitorDataAdmin, self).get_queryset(request)
        return queryset.prefetch_related('content_object')


admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceData, ResourceDataAdmin)
admin.site.register(MonitorData, MonitorDataAdmin)


# Mokey-patching

def resource_inline_factory(resources):
    class ResourceInlineFormSet(generic.BaseGenericInlineFormSet):
        def total_form_count(self, resources=resources):
            return len(resources)
        
        @cached_property
        def forms(self, resources=resources):
            forms = []
            resources_copy = list(resources)
            for i, data in enumerate(self.queryset):
                forms.append(self._construct_form(i, resource=data.resource))
                resources_copy.remove(data.resource)
            for i, resource in enumerate(resources_copy, len(self.queryset)):
                forms.append(self._construct_form(i, resource=resource))
            return forms
    
    class ResourceInline(generic.GenericTabularInline):
        model = ResourceData
        verbose_name_plural = _("resources")
        form = ResourceForm
        formset = ResourceInlineFormSet
        can_delete = False
        fields = (
            'verbose_name', 'used', 'display_updated', 'allocated', 'unit'
        )
        readonly_fields = ('used', 'display_updated')
        
        class Media:
            css = {
                'all': ('orchestra/css/hide-inline-id.css',)
            }
        
        display_updated = admin_date('updated_at', default=_("Never"))
        
        def has_add_permission(self, *args, **kwargs):
            """ Hidde add another """
            return False
    return ResourceInline


def insert_resource_inlines():
    # Clean previous state
    for related in Resource._related:
        modeladmin = get_modeladmin(related)
        modeladmin_class = type(modeladmin)
        for inline in getattr(modeladmin_class, 'inlines', []):
            if inline.__name__ == 'ResourceInline':
                modeladmin_class.inlines.remove(inline)
    
    for ct, resources in Resource.objects.group_by('content_type').iteritems():
        inline = resource_inline_factory(resources)
        model = ct.model_class()
        insertattr(model, 'inlines', inline)


if database_ready():
    insert_resource_inlines()
