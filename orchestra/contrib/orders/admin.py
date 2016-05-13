from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models import Prefetch
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin 
from orchestra.admin.utils import admin_link, admin_date, change_url
from orchestra.contrib.accounts.actions import list_accounts
from orchestra.contrib.accounts.admin import AccountAdminMixin
from orchestra.utils.humanize import naturaldate

from .actions import BillSelectedOrders, mark_as_ignored, mark_as_not_ignored, report
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
            parent_id = self.parent_object.pk
            try:
                tenth_id = qs.filter(order_id=parent_id).values_list('id', flat=True)[9]
            except IndexError:
                pass
            else:
                return qs.filter(pk__gte=tenth_id)
        return qs


class OrderAdmin(AccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'display_description', 'service_link', 'account_link', 'content_object_link',
        'display_registered_on', 'display_billed_until', 'display_cancelled_on',
        'display_metric'
    )
    list_filter = (
        ActiveOrderListFilter, IgnoreOrderListFilter, BilledOrderListFilter, 'account__type',
        'service',
    )
    default_changelist_filters = (
        ('ignore', '0'),
    )
    actions = (
        BillSelectedOrders(), mark_as_ignored, mark_as_not_ignored, report, list_accounts
    )
    change_view_actions = (BillSelectedOrders(), mark_as_ignored, mark_as_not_ignored)
    date_hierarchy = 'registered_on'
    inlines = (MetricStorageInline,)
    add_inlines = ()
    search_fields = ('account__username', 'content_object_repr', 'description',)
    list_prefetch_related = (
        'content_object',
        Prefetch('metrics', queryset=MetricStorage.objects.order_by('-id')),
    )
    list_select_related = ('account', 'service')
    add_fieldsets = (
        (None, {
            'fields': ('account', 'service')
        }),
        (_("Object"), {
            'fields': ('content_type', 'object_id',),
        }),
        (_("State"), {
            'fields': ('registered_on', 'cancelled_on', 'billed_on', 'billed_metric',
                       'billed_until' )
        }),
        (None, {
            'fields': ('description', 'ignore',),
        }),
    )
    fieldsets = (
        (None, {
            'fields': ('account_link', 'service_link', 'content_object_link'),
        }),
        (_("State"), {
            'fields': ('registered_on', 'cancelled_on', 'billed_on', 'billed_metric',
                       'billed_until' )
        }),
        (None, {
            'fields': ('description', 'ignore', 'bills_links'),
        }),
    )
    readonly_fields = (
        'content_object_repr', 'content_object_link', 'bills_links', 'account_link',
        'service_link'
    )
    
    service_link = admin_link('service')
    display_registered_on = admin_date('registered_on')
    display_cancelled_on = admin_date('cancelled_on')
    
    def display_description(self, order):
        return order.description[:64]
    display_description.short_description = _("Description")
    display_description.allow_tags = True
    display_description.admin_order_field = 'description'
    
    def content_object_link(self, order):
        if order.content_object:
            try:
                url = change_url(order.content_object)
            except NoReverseMatch:
                # Does not has admin
                return order.content_object_repr
            description = str(order.content_object)
            return '<a href="{url}">{description}</a>'.format(
                url=url, description=description)
        return order.content_object_repr
    content_object_link.short_description = _("Content object")
    content_object_link.allow_tags = True
    content_object_link.admin_order_field = 'content_object_repr'
    
    def bills_links(self, order):
        bills = []
        make_link = admin_link()
        for line in order.lines.select_related('bill').distinct('bill'):
            bills.append(make_link(line.bill))
        return '<br>'.join(bills)
    bills_links.short_description = _("Bills")
    bills_links.allow_tags = True
    
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
        """
        dispalys latest metric value, don't uses latest() because not loosing prefetch_related
        """
        try:
            metric = order.metrics.all()[0]
        except IndexError:
            return ''
        return metric.value
    display_metric.short_description = _("Metric")
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'description':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 2})
        return super().formfield_for_dbfield(db_field, **kwargs)

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
    raw_id_fields = ('order',)


admin.site.register(Order, OrderAdmin)
admin.site.register(MetricStorage, MetricStorageAdmin)
