from django.conf.urls import patterns, url
from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.utils.translation import ungettext, ugettext, ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.filters import UsedContentTypeFilter
from orchestra.admin.utils import insertattr, get_modeladmin, admin_link, admin_date
from orchestra.contrib.orchestration.models import Route
from orchestra.core import services
from orchestra.utils import database_ready

from .actions import run_monitor
from .forms import ResourceForm
from .models import Resource, ResourceData, MonitorData


class ResourceAdmin(ExtendedModelAdmin):
    list_display = (
        'id', 'verbose_name', 'content_type', 'aggregation', 'on_demand',
        'default_allocation', 'unit', 'crontab', 'is_active'
    )
    list_display_links = ('id', 'verbose_name')
    list_editable = ('default_allocation', 'crontab', 'is_active',)
    list_filter = (UsedContentTypeFilter, 'aggregation', 'on_demand', 'disable_trigger')
    fieldsets = (
        (None, {
            'fields': ('verbose_name', 'name', 'content_type', 'aggregation'),
        }),
        (_("Configuration"), {
            'fields': ('unit', 'scale', 'on_demand', 'default_allocation', 'disable_trigger',
                       'is_active'),
        }),
        (_("Monitoring"), {
            'fields': ('monitors', 'crontab'),
        }),
    )
    actions = (run_monitor,)
    change_view_actions = actions
    change_readonly_fields = ('name', 'content_type')
    prepopulated_fields = {'name': ('verbose_name',)}
    list_select_related = ('content_type', 'crontab',)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Remaind user when monitor routes are not configured """
        if request.method == 'GET':
            resource = self.get_object(request, unquote(object_id))
            backends = Route.objects.values_list('backend', flat=True)
            not_routed = []
            for monitor in resource.monitors:
                if monitor not in backends:
                    not_routed.append(monitor)
            if not_routed:
                messages.warning(request, ungettext(
                    _("%(not_routed)s monitor doesn't have any configured route."),
                    _("%(not_routed)s monitors don't have any configured route."),
                    len(not_routed),
                ) % {
                    'not_routed': ', '.join(not_routed)
                })
        return super(ResourceAdmin, self).change_view(request, object_id, form_url=form_url,
                extra_context=extra_context)
    
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
        'id', 'resource_link', 'content_object_link', 'allocated', 'display_used', 'display_unit',
        'display_updated'
    )
    list_filter = ('resource',)
    fields = (
        'resource_link', 'content_type', 'content_object_link', 'display_updated', 'display_used',
        'allocated', 'display_unit'
    )
    search_fields = ('object_id',)
    readonly_fields = fields
    actions = (run_monitor,)
    change_view_actions = actions
    ordering = ('-updated_at',)
    list_select_related = ('resource__content_type',)
    list_prefetch_related = ('content_object',)
    
    resource_link = admin_link('resource')
    content_object_link = admin_link('content_object')
    content_object_link.admin_order_field = None
    display_updated = admin_date('updated_at', short_description=_("Updated"))
    
    def get_urls(self):
        """Returns the additional urls for the change view links"""
        urls = super(ResourceDataAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        return patterns('',
            url('^(\d+)/used-monitordata/$',
                admin_site.admin_view(self.used_monitordata_view),
                name='%s_%s_used_monitordata' % (opts.app_label, opts.model_name)
            )
        ) + urls
    
    def display_unit(self, data):
        return data.unit
    display_unit.short_description = _("Unit")
    display_unit.admin_order_field = 'resource__unit'
    
    def display_used(self, data):
        if not data.used:
            return ''
        url = reverse('admin:resources_resourcedata_used_monitordata', args=(data.pk,))
        return '<a href="%s">%s</a>' % (url, data.used)
    display_used.short_description = _("Used")
    display_used.admin_order_field = 'used'
    display_used.allow_tags = True
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def used_monitordata_view(self, request, object_id):
        """
        Does the redirect on a separated view for performance reassons
        (calculate this on a changelist is expensive)
        """
        data = self.get_object(request, object_id)
        ids = []
        for dataset in data.get_monitor_datasets():
            if isinstance(dataset, MonitorData):
                ids.append(dataset.id)
            else:
                ids += dataset.values_list('id', flat=True)
        url = reverse('admin:resources_monitordata_changelist')
        url += '?id__in=%s' % ','.join(map(str, ids))
        return redirect(url)


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
        
        def get_queryset(self):
            """ Filter disabled resources """
            queryset = super(ResourceInlineFormSet, self).get_queryset()
            return queryset.filter(resource__is_active=True)
        
        @cached_property
        def forms(self, resources=resources):
            forms = []
            resources_copy = list(resources)
            # Remove queryset disabled objects
            queryset = [data for data in self.get_queryset() if data.resource in resources]
            if self.instance.pk:
                # Create missing resource data
                queryset_resources = [data.resource for data in queryset]
                for resource in resources:
                    if resource not in queryset_resources:
                        kwargs = {
                            'content_object': self.instance,
                        }
                        if resource.default_allocation:
                            kwargs['allocated'] = resource.default_allocation
                        data = resource.dataset.create(**kwargs)
                        queryset.append(data)
            # Existing dataset
            for i, data in enumerate(queryset):
                forms.append(self._construct_form(i, resource=data.resource))
                try:
                    resources_copy.remove(data.resource)
                except ValueError:
                    pass
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
        display_used.allow_tags = True
        
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
    resources = Resource.objects.filter(is_active=True)
    for ct, resources in resources.group_by('content_type').items():
        inline = resource_inline_factory(resources)
        model = ct.model_class()
        insertattr(model, 'inlines', inline)


if database_ready():
    insert_resource_inlines()
