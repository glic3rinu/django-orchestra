from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.actions import disable, enable
from orchestra.admin.utils import admin_link
from orchestra.contrib.accounts.admin import AccountAdminMixin
from orchestra.contrib.accounts.filters import IsActiveListFilter
from orchestra.plugins import PluginModelAdapter
from orchestra.plugins.admin import SelectPluginAdminMixin
from orchestra.utils.python import import_class

from . import settings
from .models import MiscService, Miscellaneous


class MiscServicePlugin(PluginModelAdapter):
    model = MiscService
    name_field = 'name'
    plugin_field = 'service'


class MiscServiceAdmin(ExtendedModelAdmin):
    list_display = (
        'display_name', 'display_verbose_name', 'num_instances', 'has_identifier', 'has_amount', 'is_active'
    )
    list_editable = ('is_active',)
    list_filter = ('has_identifier', 'has_amount', IsActiveListFilter)
    fields = (
        'verbose_name', 'name', 'description', 'has_identifier', 'has_amount', 'is_active'
    )
    prepopulated_fields = {'name': ('verbose_name',)}
    change_readonly_fields = ('name',)
    actions = (disable, enable)
    
    def display_name(self, misc):
        return '<span title="%s">%s</span>' % (misc.description, misc.name)
    display_name.short_description = _("name")
    display_name.allow_tags = True
    display_name.admin_order_field = 'name'
    
    def display_verbose_name(self, misc):
        return '<span title="%s">%s</span>' % (misc.description, misc.verbose_name)
    display_verbose_name.short_description = _("verbose name")
    display_verbose_name.allow_tags = True
    display_verbose_name.admin_order_field = 'verbose_name'
    
    def num_instances(self, misc):
        """ return num slivers as a link to slivers changelist view """
        num = misc.instances__count
        url = reverse('admin:miscellaneous_miscellaneous_changelist')
        url += '?service__name={}'.format(misc.name)
        return mark_safe('<a href="{0}">{1}</a>'.format(url, num))
    num_instances.short_description = _("Instances")
    num_instances.admin_order_field = 'instances__count'
    
    def get_queryset(self, request):
        qs = super(MiscServiceAdmin, self).get_queryset(request)
        return qs.annotate(models.Count('instances', distinct=True))
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'description':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 2})
        return super(MiscServiceAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class MiscellaneousAdmin(SelectPluginAdminMixin, AccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        '__str__', 'service_link', 'amount', 'account_link', 'dispaly_active'
    )
    list_filter = ('service__name', 'is_active')
    list_select_related = ('service', 'account')
    readonly_fields = ('account_link', 'service_link')
    add_fields = ('service', 'account', 'description', 'is_active')
    fields = ('service_link', 'account', 'description', 'is_active')
    change_readonly_fields = ('identifier', 'service')
    search_fields = ('identifier', 'description', 'account__username')
    actions = (disable, enable)
    plugin_field = 'service'
    plugin = MiscServicePlugin
    
    service_link = admin_link('service')
    
    def dispaly_active(self, instance):
        return instance.active
    dispaly_active.short_description = _("Active")
    dispaly_active.boolean = True
    dispaly_active.admin_order_field = 'is_active'
    
    def get_service(self, obj):
        if obj is None:
            return self.plugin.get(self.plugin_value).related_instance
        else:
            return obj.service
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fields = list(fieldsets[0][1]['fields'])
        service = self.get_service(obj)
        if obj:
            fields.insert(1, 'account_link')
        if service.has_amount:
            fields.insert(-1, 'amount')
        if service.has_identifier:
            fields.insert(2, 'identifier')
        fieldsets[0][1]['fields'] = fields
        return fieldsets
    
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            plugin = self.plugin.get(obj.service.name)()
        else:
            plugin = self.plugin.get(self.plugin_value)()
        self.form = plugin.get_form()
        self.plugin_instance = plugin
        service = self.get_service(obj)
        form = super(SelectPluginAdminMixin, self).get_form(request, obj, **kwargs)
        def clean_identifier(self, service=service):
            identifier = self.cleaned_data['identifier']
            validator_path = settings.MISCELLANEOUS_IDENTIFIER_VALIDATORS.get(service.name, None)
            if validator_path:
                validator = import_class(validator_path)
                validator(identifier)
            return identifier
        
        form.clean_identifier = clean_identifier
        return form
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'description':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 4})
        return super(MiscellaneousAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if not change:
            plugin = self.plugin
            kwargs = {
                plugin.name_field: self.plugin_value
            }
            setattr(obj, self.plugin_field, plugin.model.objects.get(**kwargs))
        obj.save()


admin.site.register(MiscService, MiscServiceAdmin)
admin.site.register(Miscellaneous, MiscellaneousAdmin)
