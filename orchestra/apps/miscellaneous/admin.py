from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.apps.accounts.admin import AccountAdminMixin

from .models import MiscService, Miscellaneous


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


class MiscellaneousAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = ('service', 'amount', 'active', 'account_link')
    
    def get_fields(self, request, obj=None):
        if obj is None:
            return ('service', 'account', 'description', 'amount', 'is_active')
        elif not obj.service.has_amount:
            return ('service', 'account_link', 'description', 'is_active')
        return ('service', 'account_link', 'description', 'amount', 'is_active')


admin.site.register(MiscService, MiscServiceAdmin)
admin.site.register(Miscellaneous, MiscellaneousAdmin)
