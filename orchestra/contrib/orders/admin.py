from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import Prefetch
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin 
from orchestra.admin.utils import admin_link, admin_date
from orchestra.contrib.accounts.admin import AccountAdminMixin
from orchestra.utils.humanize import naturaldate

from .actions import BillSelectedOrders, mark_as_ignored, mark_as_not_ignored
from .filters import IgnoreOrderListFilter, ActiveOrderListFilter, BilledOrderListFilter
from .models import Order, MetricStorage


class MetricStorageInline(admin.TabularInline):
    model = MetricStorage
    readonly_fields = ('value', 'created_on', 'updated_on')
    extra = 0
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def get_fieldsets(self, request, obj=None):
        if obj:
             url = reverse('admin:orders_metricstorage_changelist')
             url += '?order=%i' % obj.pk
             title = _('Metric storage, last 10 entries, <a href="%s">(See all)</a>')
             self.verbose_name_plural = mark_safe(title % url)
        return super(MetricStorageInline, self).get_fieldsets(request, obj)
    
    def get_queryset(self, request):
        qs = super(MetricStorageInline, self).get_queryset(request)
        change_view = bool(self.parent_object and self.parent_object.pk)
        if change_view:
            qs = qs.order_by('-id')
            try:
                tenth_id = qs.values_list('id', flat=True)[9]
            except IndexError:
                pass
            else:
                return qs.filter(pk__lte=tenth_id)
        return qs


class OrderAdmin(AccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'id', 'service_link', 'account_link', 'content_object_link',
        'display_registered_on', 'display_billed_until', 'display_cancelled_on', 'display_metric'
    )
    list_filter = (ActiveOrderListFilter, IgnoreOrderListFilter, BilledOrderListFilter, 'service')
    default_changelist_filters = (
        ('ignore', '0'),
    )
    actions = (BillSelectedOrders(), mark_as_ignored, mark_as_not_ignored)
    change_view_actions = (BillSelectedOrders(), mark_as_ignored, mark_as_not_ignored)
    date_hierarchy = 'registered_on'
    inlines = (MetricStorageInline,)
    add_inlines = ()
    search_fields = ('account__username', 'description')
    list_prefetch_related = (
        'content_object',
        Prefetch('metrics', queryset=MetricStorage.objects.order_by('-id')),
    )
    list_select_related = ('account', 'service')
    
    service_link = admin_link('service')
    content_object_link = admin_link('content_object', order=False)
    display_registered_on = admin_date('registered_on')
    display_cancelled_on = admin_date('cancelled_on')
    
    def display_billed_until(self, order):
        billed_until = order.billed_until
        red = False
        human = escape(naturaldate(billed_until))
        if billed_until:
            if order.cancelled_on and order.cancelled_on <= billed_until:
                pass
            elif order.service.billing_period == order.service.NEVER:
                human = _("Forever")
            elif order.service.payment_style == order.service.POSTPAY:
                boundary = order.service.handler.get_billing_point(order)
                if billed_until < boundary:
                    red = True
            elif billed_until < timezone.now().date():
                red = True
        color = 'style="color:red;"' if red else ''
        return '<span title="{raw}" {color}>{human}</span>'.format(
            raw=escape(str(billed_until)), color=color, human=human,
        )
    display_billed_until.short_description = _("billed until")
    display_billed_until.allow_tags = True
    display_billed_until.admin_order_field = 'billed_until'
    
    def display_metric(self, order):
        """ dispalys latest metric value, don't uses latest() because not loosing prefetch_related """
        try:
            metric = order.metrics.all()[0]
        except IndexError:
            return ''
        return metric.value
    display_metric.short_description = _("Metric")

#    def get_changelist(self, request, **kwargs):
#        ChangeList = super(OrderAdmin, self).get_changelist(request, **kwargs)
#        class OrderFilterChangeList(ChangeList):
#            def get_filters(self, request):
#                filters = super(OrderFilterChangeList, self).get_filters(request)
#                tail = []
#                filters_copy = []
#                for list_filter in filters[0]:
#                    if getattr(list_filter, 'apply_last', False):
#                        tail.append(list_filter)
#                    else:
#                        filters_copy.append(list_filter)
#                filters = ((filters_copy+tail),) + filters[1:]
#                return filters
#        return OrderFilterChangeList


class MetricStorageAdmin(admin.ModelAdmin):
    list_display = ('order', 'value', 'created_on', 'updated_on')
    list_filter = ('order__service',)


admin.site.register(Order, OrderAdmin)
admin.site.register(MetricStorage, MetricStorageAdmin)
