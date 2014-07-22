from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.apps.accounts.admin import AccountAdminMixin

from .models import MiscService, Miscellaneous


class MiscServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_instances')
    
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
    list_display = ('service', 'amount', 'account_link')
    
    def get_fields(self, request, obj=None):
        if obj is None:
            return ('service', 'account', 'description', 'amount', 'is_active')
        if not obj.service.has_amount:
            return ('service', 'account_link', 'description', 'is_active')
        return ('service', 'account_link', 'description', 'amount', 'is_active')


admin.site.register(MiscService, MiscServiceAdmin)
admin.site.register(Miscellaneous, MiscellaneousAdmin)
