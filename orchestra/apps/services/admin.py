from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ChangeViewActionsMixin
from orchestra.admin.filters import UsedContentTypeFilter
from orchestra.apps.accounts.admin import AccountAdminMixin
from orchestra.core import services

from .actions import update_orders, view_help, clone
from .models import Plan, ContractedPlan, Rate, Service


class RateInline(admin.TabularInline):
    model = Rate
    ordering = ('plan', 'quantity')


class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'is_combinable', 'allow_multiple')
    list_filter = ('is_default', 'is_combinable', 'allow_multiple')
    inlines = [RateInline]


class ContractedPlanAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = ('plan', 'account_link')
    list_filter = ('plan__name',)


class ServiceAdmin(ChangeViewActionsMixin, admin.ModelAdmin):
    list_display = (
        'description', 'content_type', 'handler_type', 'num_orders', 'is_active'
    )
    list_filter = ('is_active', 'handler_type', UsedContentTypeFilter)
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('description', 'content_type', 'match', 'handler_type',
                       'ignore_superusers', 'is_active')
        }),
        (_("Billing options"), {
            'classes': ('wide',),
            'fields': ('billing_period', 'billing_point', 'is_fee', 'order_description')
        }),
        (_("Pricing options"), {
            'classes': ('wide',),
            'fields': ('metric', 'pricing_period', 'rate_algorithm',
                       'on_cancel', 'payment_style', 'tax', 'nominal_price')
        }),
    )
    inlines = [RateInline]
    actions = [update_orders, clone]
    change_view_actions = actions + [view_help]
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Improve performance of account field and filter by account """
        if db_field.name == 'content_type':
            models = [model._meta.model_name for model in services.get()]
            queryset = db_field.rel.to.objects
            kwargs['queryset'] = queryset.filter(model__in=models)
        if db_field.name in ['match', 'metric', 'order_description']:
            kwargs['widget'] = forms.TextInput(attrs={'size':'160'})
        return super(ServiceAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def num_orders(self, service):
        num = service.orders__count
        url = reverse('admin:orders_order_changelist')
        url += '?service=%i&is_active=True' % service.pk
        return '<a href="%s">%d</a>' % (url, num)
    num_orders.short_description = _("Orders")
    num_orders.admin_order_field = 'orders__count'
    num_orders.allow_tags = True
    
    def get_queryset(self, request):
        qs = super(ServiceAdmin, self).get_queryset(request)
        # Count active orders
        qs = qs.extra(select={
            'orders__count': (
                "SELECT COUNT(*) "
                "FROM orders_order "
                "WHERE orders_order.service_id = services_service.id AND ("
                "      orders_order.cancelled_on IS NULL OR"
                "      orders_order.cancelled_on > '%s' "
                ")" % timezone.now()
            )
        })
        return qs


admin.site.register(Plan, PlanAdmin)
admin.site.register(ContractedPlan, ContractedPlanAdmin)
admin.site.register(Service, ServiceAdmin)
