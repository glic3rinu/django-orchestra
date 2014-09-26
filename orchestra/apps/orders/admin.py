from django.contrib import admin
from django.utils import timezone
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import admin_link, admin_date
from orchestra.apps.accounts.admin import AccountAdminMixin
from orchestra.utils.humanize import naturaldate

from .actions import BillSelectedOrders
from .filters import ActiveOrderListFilter, BilledOrderListFilter
from .models import Order, MetricStorage


class OrderAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = (
        'id', 'service', 'account_link', 'content_object_link',
        'display_registered_on', 'display_billed_until', 'display_cancelled_on'
    )
    list_display_links = ('id', 'service')
    list_filter = (ActiveOrderListFilter, BilledOrderListFilter, 'service',)
    actions = (BillSelectedOrders(),)
    date_hierarchy = 'registered_on'
    
    content_object_link = admin_link('content_object', order=False)
    display_registered_on = admin_date('registered_on')
    display_cancelled_on = admin_date('cancelled_on')
    
    def display_billed_until(self, order):
        value = order.billed_until
        color = ''
        if value and value < timezone.now():
            color = 'style="color:red;"'
        return '<span title="{raw}" {color}>{human}</span>'.format(
            raw=escape(str(value)), color=color, human=escape(naturaldate(value)),
        )
    display_billed_until.short_description = _("billed until")
    display_billed_until.allow_tags = True
    display_billed_until.admin_order_field = 'billed_until'
    
    def get_queryset(self, request):
        qs = super(OrderAdmin, self).get_queryset(request)
        return qs.select_related('service').prefetch_related('content_object')


class MetricStorageAdmin(admin.ModelAdmin):
    list_display = ('order', 'value', 'created_on', 'updated_on')
    list_filter = ('order__service',)


admin.site.register(Order, OrderAdmin)
admin.site.register(MetricStorage, MetricStorageAdmin)
