from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ChangeViewActionsMixin
from orchestra.admin.actions import disable, enable
from orchestra.core import services

from .actions import update_orders, view_help, clone
from .models import Service


class ServiceAdmin(ChangeViewActionsMixin, admin.ModelAdmin):
    list_display = (
        'description', 'content_type', 'handler_type', 'num_orders', 'is_active'
    )
    list_filter = (
        'is_active', 'handler_type', 'is_fee',
        ('content_type', admin.RelatedOnlyFieldListFilter),
    )
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('description', 'content_type', 'match', 'periodic_update',
                       'handler_type', 'ignore_superusers', 'is_active')
        }),
        (_("Billing options"), {
            'classes': ('wide',),
            'fields': ('billing_period', 'billing_point', 'is_fee', 'order_description',
                       'ignore_period')
        }),
        (_("Pricing options"), {
            'classes': ('wide',),
            'fields': ('metric', 'pricing_period', 'rate_algorithm',
                       'on_cancel', 'payment_style', 'tax', 'nominal_price')
        }),
    )
    actions = (update_orders, clone, disable, enable)
    change_view_actions = actions + (view_help,)
    change_form_template = 'admin/services/service/change_form.html'
    
    def get_urls(self):
        """Returns the additional urls for the change view links"""
        urls = super(ServiceAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        return [
            url('^add/help/$',
                admin_site.admin_view(self.help_view),
                name='%s_%s_help' % (opts.app_label, opts.model_name)
            )
        ] + urls
    
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
        url += '?service__id__exact=%i&is_active=True' % service.pk
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
    
    def help_view(self, request, *args):
        opts = self.model._meta
        context = {
            'add': True,
            'title': _("Need some help?"),
            'opts': opts,
            'obj': args[0].get() if args else None,
            'action_name': _("help"),
            'app_label': opts.app_label,
        }
        return TemplateResponse(request, 'admin/services/service/help.html', context)
    help_view.url_name = 'help'
    help_view.verbose_name = _("Help")


admin.site.register(Service, ServiceAdmin)
