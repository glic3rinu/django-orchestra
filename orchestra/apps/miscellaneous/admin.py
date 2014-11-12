from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.apps.accounts.admin import AccountAdminMixin

from .models import MiscService, Miscellaneous


from orchestra.apps.plugins.admin import SelectPluginAdminMixin, PluginAdapter


class MiscServicePlugin(PluginAdapter):
    model = MiscService
    name_field = 'name'


class MiscServiceAdmin(ExtendedModelAdmin):
    list_display = ('name', 'verbose_name', 'num_instances', 'has_amount', 'is_active')
    list_editable = ('has_amount', 'is_active')
    list_filter = ('has_amount', 'is_active')
    fields = ('verbose_name', 'name', 'description', 'has_amount', 'is_active')
    prepopulated_fields = {'name': ('verbose_name',)}
    change_readonly_fields = ('name',)
    
    def num_instances(self, misc):
        """ return num slivers as a link to slivers changelist view """
        num = misc.instances__count
        url = reverse('admin:miscellaneous_miscellaneous_changelist')
        url += '?service={}'.format(misc.pk)
        return mark_safe('<a href="{0}">{1}</a>'.format(url, num))
    num_instances.short_description = _("Instances")
    num_instances.admin_order_field = 'instances__count'
    
    def get_queryset(self, request):
        qs = super(MiscServiceAdmin, self).queryset(request)
        return qs.annotate(models.Count('instances', distinct=True))


class MiscellaneousAdmin(AccountAdminMixin, SelectPluginAdminMixin, admin.ModelAdmin):
    list_display = ('service', 'amount', 'active', 'account_link')
    plugin_field = 'service'
    plugin = MiscServicePlugin
    
    def get_service(self, obj):
        if obj is None:
            return self.plugin.get_plugin(self.plugin_value)().instance
        else:
            return obj.service
    
    def get_fields(self, request, obj=None):
        fields = ['account', 'description', 'is_active']
        if obj is not None:
            fields = ['account_link', 'description', 'is_active']
        service = self.get_service(obj)
        if service.has_amount:
            fields.insert(-1, 'amount')
#        if service.has_identifier:
#            fields.insert(1, 'identifier')
        return fields
    
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(SelectPluginAdminMixin, self).get_form(request, obj=obj, **kwargs)
        service = self.get_service(obj)
        def clean_identifier(self, service=service):
            validator = settings.MISCELLANEOUS_IDENTIFIER_VALIDATORS.get(service.name, None)
            if validator:
                validator(self.cleaned_data['identifier'])
        form.clean_identifier = clean_identifier
        return form


admin.site.register(MiscService, MiscServiceAdmin)
admin.site.register(Miscellaneous, MiscellaneousAdmin)
