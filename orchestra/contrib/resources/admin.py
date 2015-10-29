from urllib.parse import parse_qs

from django.apps import apps
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet
from django.contrib.admin.utils import unquote
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import redirect
from django.templatetags.static import static
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import insertattr, get_modeladmin, admin_link, admin_date
from orchestra.contrib.orchestration.models import Route
from orchestra.core import services
from orchestra.utils import db, sys
from orchestra.utils.functional import cached

from .actions import run_monitor, show_history
from .api import history_data
from .filters import ResourceDataListFilter
from .forms import ResourceForm
from .models import Resource, ResourceData, MonitorData


class ResourceAdmin(ExtendedModelAdmin):
    list_display = (
        'id', 'verbose_name', 'content_type', 'aggregation', 'on_demand',
        'default_allocation', 'unit', 'crontab', 'is_active'
    )
    list_display_links = ('id', 'verbose_name')
    list_editable = ('default_allocation', 'crontab', 'is_active',)
    list_filter = (
        ('content_type', admin.RelatedOnlyFieldListFilter), 'aggregation', 'on_demand',
        'disable_trigger'
    )
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
    prepopulated_fields = {
        'name': ('verbose_name',)
    }
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
        # best-effort
        model = obj.content_type.model_class()
        modeladmin = type(get_modeladmin(model))
        resources = obj.content_type.resource_set.filter(is_active=True)
        inlines = []
        for inline in modeladmin.inlines:
            if inline.model is ResourceData:
                inline = resource_inline_factory(resources)
            inlines.append(inline)
        modeladmin.inlines = inlines
        # reload Not always work
        sys.touch_wsgi()
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ filter service content_types """
        if db_field.name == 'content_type':
            models = [ model._meta.model_name for model in services.get() ]
            kwargs['queryset'] = db_field.rel.to.objects.filter(model__in=models)
        return super(ResourceAdmin, self).formfield_for_dbfield(db_field, **kwargs)


def content_object_link(data):
    ct = data.content_type
    url = reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=(data.object_id,))
    return '<a href="%s">%s</a>' % (url, data.content_object_repr)
content_object_link.short_description = _("Content object")
content_object_link.admin_order_field = 'content_object_repr'
content_object_link.allow_tags = True


class ResourceDataAdmin(ExtendedModelAdmin):
    list_display = (
        'id', 'resource_link', content_object_link, 'allocated', 'display_used',
        'display_updated'
    )
    list_filter = ('resource',)
    fields = (
        'resource_link', 'content_type', content_object_link, 'display_updated', 'display_used',
        'allocated',
    )
    search_fields = ('content_object_repr',)
    readonly_fields = fields
    actions = (run_monitor, show_history)
    change_view_actions = actions
    ordering = ('-updated_at',)
    list_select_related = ('resource__content_type', 'content_type')
    
    resource_link = admin_link('resource')
    display_updated = admin_date('updated_at', short_description=_("Updated"))
    
    def get_urls(self):
        """Returns the additional urls for the change view links"""
        urls = super(ResourceDataAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        return [
            url('^(\d+)/used-monitordata/$',
                admin_site.admin_view(self.used_monitordata_view),
                name='%s_%s_used_monitordata' % (opts.app_label, opts.model_name)
            ),
            url('^history_data/$',
                admin_site.admin_view(history_data),
                name='%s_%s_history_data' % (opts.app_label, opts.model_name)
            ),
            url('^list-related/(.+)/(.+)/(\d+)/$',
                admin_site.admin_view(self.list_related_view),
                name='%s_%s_list_related' % (opts.app_label, opts.model_name)
            ),
        ] + urls
    
    def display_used(self, rdata):
        if rdata.used is None:
            return ''
        url = reverse('admin:resources_resourcedata_used_monitordata', args=(rdata.pk,))
        return '<a href="%s">%s %s</a>' % (url, rdata.used, rdata.unit)
    display_used.short_description = _("Used")
    display_used.admin_order_field = 'used'
    display_used.allow_tags = True
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def used_monitordata_view(self, request, object_id):
        url = reverse('admin:resources_monitordata_changelist')
        url += '?resource_data=%s' % object_id
        return redirect(url)
    
    def list_related_view(self, request, app_name, model_name, object_id):
        resources = Resource.objects.select_related('content_type')
        resource_models = {r.content_type.model_class(): r.content_type_id for r in resources}
        # Self
        model = apps.get_model(app_name, model_name)
        obj = model.objects.get(id=int(object_id))
        ct_id = resource_models[model]
        qset = Q(content_type_id=ct_id, object_id=obj.id, resource__is_active=True)
        # Related
        for field, rel in obj._meta.fields_map.items():
            try:
                ct_id = resource_models[rel.related_model]
            except KeyError:
                pass
            else:
                manager = getattr(obj, field)
                ids = manager.values_list('id', flat=True)
                qset = Q(qset) | Q(content_type_id=ct_id, object_id__in=ids, resource__is_active=True)
        related = ResourceData.objects.filter(qset)
        related_ids = related.values_list('id', flat=True)
        related_ids = ','.join(map(str, related_ids))
        url = reverse('admin:resources_resourcedata_changelist')
        url += '?id__in=%s' % related_ids
        return redirect(url)


class MonitorDataAdmin(ExtendedModelAdmin):
    list_display = ('id', 'monitor', content_object_link, 'display_created', 'value')
    list_filter = ('monitor', ResourceDataListFilter)
    add_fields = ('monitor', 'content_type', 'object_id', 'created_at', 'value')
    fields = ('monitor', 'content_type', content_object_link, 'display_created', 'value', 'state')
    change_readonly_fields = fields
    list_select_related = ('content_type',)
    search_fields = ('content_object_repr',)
    date_hierarchy = 'created_at'
    
    display_created = admin_date('created_at', short_description=_("Created"))
    
    def filter_used_monitordata(self, request, queryset):
        query_string = parse_qs(request.META['QUERY_STRING'])
        resource_data = query_string.get('resource_data')
        if resource_data:
            mdata = ResourceData.objects.get(pk=int(resource_data[0]))
            resource = mdata.resource
            ids = []
            for monitor, dataset in mdata.get_monitor_datasets():
                dataset = resource.aggregation_instance.filter(dataset)
                if isinstance(dataset, MonitorData):
                    ids.append(dataset.id)
                else:
                    ids += dataset.values_list('id', flat=True)
            return queryset.filter(id__in=ids)
        return queryset
    
    def get_queryset(self, request):
        queryset = super(MonitorDataAdmin, self).get_queryset(request)
        queryset = self.filter_used_monitordata(request, queryset)
        return queryset.prefetch_related('content_object')


admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceData, ResourceDataAdmin)
admin.site.register(MonitorData, MonitorDataAdmin)


# Mokey-patching

def resource_inline_factory(resources):
    class ResourceInlineFormSet(BaseGenericInlineFormSet):
        def total_form_count(self, resources=resources):
            return len(resources)
        
        @cached
        def get_queryset(self):
            """ Filter disabled resources """
            queryset = super(ResourceInlineFormSet, self).get_queryset()
            return queryset.filter(resource__is_active=True).select_related('resource')
        
        @cached_property
        def forms(self, resources=resources):
            forms = []
            resources_copy = list(resources)
            # Remove queryset disabled objects
            queryset = [rdata for rdata in self.get_queryset() if rdata.resource in resources]
            if self.instance.pk:
                # Create missing resource data
                queryset_resources = [rdata.resource for rdata in queryset]
                for resource in resources:
                    if resource not in queryset_resources:
                        kwargs = {
                            'content_object': self.instance,
                            'content_object_repr': str(self.instance),
                        }
                        if resource.default_allocation:
                            kwargs['allocated'] = resource.default_allocation
                        rdata = resource.dataset.create(**kwargs)
                        queryset.append(rdata)
            # Existing dataset
            for i, rdata in enumerate(queryset):
                forms.append(self._construct_form(i, resource=rdata.resource))
                try:
                    resources_copy.remove(rdata.resource)
                except ValueError:
                    pass
            # Missing dataset
            for i, resource in enumerate(resources_copy, len(queryset)):
                forms.append(self._construct_form(i, resource=resource))
            return forms
    
    class ResourceInline(GenericTabularInline):
        model = ResourceData
        verbose_name_plural = _("resources")
        form = ResourceForm
        formset = ResourceInlineFormSet
        can_delete = False
        fields = (
            'verbose_name', 'display_used', 'display_updated', 'allocated', 'unit',
        )
        readonly_fields = ('display_used', 'display_updated',)
        
        class Media:
            css = {
                'all': ('orchestra/css/hide-inline-id.css',)
            }
        
        display_updated = admin_date('updated_at', default=_("Never"))
        
        def get_fieldsets(self, request, obj=None):
            if obj:
                opts = self.parent_model._meta
                url = reverse('admin:resources_resourcedata_list_related',
                    args=(opts.app_label, opts.model_name, obj.id))
                link = '<a href="%s">%s</a>' % (url, _("List related"))
                self.verbose_name_plural = mark_safe(_("Resources") + ' ' + link)
            return super(ResourceInline, self).get_fieldsets(request, obj)
        
        def display_used(self, rdata):
            update = ''
            history = ''
            if rdata.pk:
                context = {
                    'title': _("Update"),
                    'url': reverse('admin:resources_resourcedata_monitor', args=(rdata.pk,)),
                    'image': '<img src="%s"></img>' % static('orchestra/images/reload.png'),
                }
                update = '<a href="%(url)s" title="%(title)s">%(image)s</a>' % context
                context.update({
                    'title': _("Show history"),
                    'image': '<img src="%s"></img>' % static('orchestra/images/history.png'),
                    'url': reverse('admin:resources_resourcedata_show_history', args=(rdata.pk,)),
                    'popup': 'onclick="return showAddAnotherPopup(this);"',
                })
                history = '<a href="%(url)s" title="%(title)s" %(popup)s>%(image)s</a>' % context
            if rdata.used is not None:
                used_url = reverse('admin:resources_resourcedata_used_monitordata', args=(rdata.pk,))
                used =  '<a href="%s">%s %s</a>' % (used_url, rdata.used, rdata.unit)
                return ' '.join(map(str, (used, update, history)))
            if rdata.resource.monitors:
                return _("Unknonw %s %s") % (update, history)
            return _("No monitor")
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


if db.database_ready():
    insert_resource_inlines()
