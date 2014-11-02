from django.contrib import admin, messages
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.filters import UsedContentTypeFilter
from orchestra.admin.utils import insertattr, get_modeladmin, admin_link, admin_date
from orchestra.core import services
from orchestra.utils import database_ready

from .actions import run_monitor
from .forms import ResourceForm
from .models import Resource, ResourceData, MonitorData


class ResourceAdmin(ExtendedModelAdmin):
    list_display = (
        'id', 'verbose_name', 'content_type', 'period', 'on_demand',
        'default_allocation', 'unit', 'crontab', 'is_active'
    )
    list_display_links = ('id', 'verbose_name')
    list_editable = ('default_allocation', 'crontab', 'is_active',)
    list_filter = (UsedContentTypeFilter, 'period', 'on_demand', 'disable_trigger')
    fieldsets = (
        (None, {
            'fields': ('verbose_name', 'name', 'content_type', 'period'),
        }),
        (_("Configuration"), {
            'fields': ('unit', 'scale', 'on_demand', 'default_allocation', 'disable_trigger',
                       'is_active'),
        }),
        (_("Monitoring"), {
            'fields': ('monitors', 'crontab'),
        }),
    )
    change_readonly_fields = ('name', 'content_type', 'period')
    prepopulated_fields = {'name': ('verbose_name',)}
    
    def add_view(self, request, **kwargs):
        """ Warning user if the node is not fully configured """
        if request.method == 'POST':
            messages.warning(request, mark_safe(_(
                "Restarting orchestra and celerybeat is required to fully apply changes.<br> "
                "Remember that new allocated values will be applied when objects are saved."
            )))
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


class ResourceDataAdmin(ExtendedModelAdmin):
    list_display = (
        'id', 'resource_link', 'content_object_link', 'used', 'allocated', 'display_unit',
        'display_updated'
    )
    list_filter = ('resource',)
    add_fields = ('resource', 'content_type', 'object_id', 'used', 'updated_at', 'allocated')
    fields = (
        'resource_link', 'content_type', 'content_object_link', 'used', 'display_updated',
        'allocated', 'display_unit'
    )
    readonly_fields = ('display_unit',)
    change_readonly_fields = (
        'resource_link', 'content_type', 'content_object_link', 'used', 'display_updated',
        'display_unit'
    )
    actions = (run_monitor,)
    change_view_actions = actions
    ordering = ('-updated_at',)
    prefetch_related = ('content_object',)

    resource_link = admin_link('resource')
    content_object_link = admin_link('content_object')
    display_updated = admin_date('updated_at', short_description=_("Updated"))
    
    def display_unit(self, data):
        return data.unit
    display_unit.short_description = _("Unit")
    display_unit.admin_order_field = 'resource__unit'


class MonitorDataAdmin(ExtendedModelAdmin):
    list_display = ('id', 'monitor', 'display_created', 'value', 'content_object_link')
    list_filter = ('monitor',)
    add_fields = ('monitor', 'content_type', 'object_id', 'created_at', 'value')
    fields = ('monitor', 'content_type', 'content_object_link', 'display_created', 'value')
    change_readonly_fields = fields
    
    content_object_link = admin_link('content_object')
    display_created = admin_date('created_at', short_description=_("Created"))
    
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
            queryset = self.queryset
            if self.instance.pk:
                # Create missing resource data
                queryset = list(queryset)
                queryset_resources = [data.resource for data in queryset]
                for resource in resources:
                    if resource not in queryset_resources:
                        data = resource.dataset.create(content_object=self.instance)
                        queryset.append(data)
            # Existing dataset
            for i, data in enumerate(queryset):
                forms.append(self._construct_form(i, resource=data.resource))
                resources_copy.remove(data.resource)
            # Missing dataset
            for i, resource in enumerate(resources_copy, len(queryset)):
                forms.append(self._construct_form(i, resource=resource))
            return forms
    
    class ResourceInline(generic.GenericTabularInline):
        model = ResourceData
        verbose_name_plural = _("resources")
        form = ResourceForm
        formset = ResourceInlineFormSet
        can_delete = False
        fields = (
            'verbose_name', 'display_used', 'display_updated', 'allocated', 'unit',
        )
        readonly_fields = ('display_used', 'display_updated')
        
        class Media:
            css = {
                'all': ('orchestra/css/hide-inline-id.css',)
            }
        
        display_updated = admin_date('updated_at', default=_("Never"))
        
        def display_used(self, data):
            update_link = ''
            if data.pk:
                url = reverse('admin:resources_resourcedata_monitor', args=(data.pk,))
                update_link = '<a href="%s"><strong>%s</strong></a>' % (url, ugettext("Update"))
            if data.used is not None:
                return '%s %s %s' % (data.used, data.resource.unit, update_link)
            return _("Unknonw %s") % update_link
        display_used.short_description = _("Used")
        
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
