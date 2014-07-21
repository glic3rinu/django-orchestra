from django import forms
from django.db import models
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ChangeListDefaultFilter
from orchestra.admin.filters import UsedContentTypeFilter
from orchestra.admin.utils import admin_link
from orchestra.apps.accounts.admin import AccountAdminMixin
from orchestra.core import services

from .filters import ActiveOrderListFilter
from .models import Service, Order, MetricStorage


class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'description', 'content_type', 'handler_type', 'num_orders', 'is_active'
    )
    list_filter = ('is_active', 'handler_type', UsedContentTypeFilter)
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('description', 'content_type', 'match', 'handler_type',
                       'is_active')
        }),
        (_("Billing options"), {
            'classes': ('wide',),
            'fields': ('billing_period', 'billing_point', 'delayed_billing',
                       'is_fee')
        }),
        (_("Pricing options"), {
            'classes': ('wide',),
            'fields': ('metric', 'pricing_period', 'rate_algorithm',
                       'orders_effect', 'on_cancel', 'payment_style',
                       'trial_period', 'refound_period', 'tax')
        }),
    )
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Improve performance of account field and filter by account """
        if db_field.name == 'content_type':
            models = [model._meta.model_name for model in services.get()]
            queryset = db_field.rel.to.objects
            kwargs['queryset'] = queryset.filter(model__in=models)
        if db_field.name in ['match', 'metric']:
            kwargs['widget'] = forms.TextInput(attrs={'size':'160'})
        return super(ServiceAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def num_orders(self, service):
        num = service.orders.count()
        url = reverse('admin:orders_order_changelist')
        url += '?service=%i' % service.pk
        return '<a href="%s">%d</a>' % (url, num)
    num_orders.short_description = _("Orders")
    num_orders.admin_order_field = 'orders__count'
    num_orders.allow_tags = True
    
    def get_queryset(self, request):
        qs = super(ServiceAdmin, self).get_queryset(request)
        qs = qs.annotate(models.Count('orders'))
        return qs


class OrderAdmin(AccountAdminMixin, ChangeListDefaultFilter, admin.ModelAdmin):
    list_display = (
        'id', 'service', 'account_link', 'content_object_link', 'cancelled_on'
    )
    list_filter = (ActiveOrderListFilter, 'service',)
    default_changelist_filters = (
        ('is_active', 'True'),
    )
    
    content_object_link = admin_link('content_object')

class MetricStorageAdmin(admin.ModelAdmin):
    list_display = ('order', 'value', 'created_on', 'updated_on')
    list_filter = ('order__service',)


admin.site.register(Service, ServiceAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(MetricStorage, MetricStorageAdmin)
