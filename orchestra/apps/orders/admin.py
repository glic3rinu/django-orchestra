from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from orchestra.core import services

from .models import Service, Order, MetricStorage


class ServiceAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('description', 'model', 'match', 'is_active')
        }),
        (_("Billing options"), {
            'classes': ('wide',),
            'fields': ('billing_period', 'billing_point', 'delayed_billing',
                       'is_fee')
        }),
        (_("Pricing options"), {
            'classes': ('wide',),
            'fields': ('metric', 'pricing_period', 'rate_algorithm',
                       'orders_effect', ('on_cancel', 'on_disable', 'on_register'),
                       'payment_style', 'trial_period', 'refound_period', 'tax',)
        }),
    )
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Improve performance of account field and filter by account """
        if db_field.name == 'model':
            models = [model._meta.model_name for model in services.get().keys()]
            kwargs['queryset'] = db_field.rel.to.objects.filter(model__in=models)
        if db_field.name in ['match', 'metric']:
            kwargs['widget'] = forms.TextInput(attrs={'size':'160'})
        return super(ServiceAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class OrderAdmin(admin.ModelAdmin):
    pass


class MetricStorageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Service, ServiceAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(MetricStorage, MetricStorageAdmin)
