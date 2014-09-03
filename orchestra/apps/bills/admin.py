from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import admin_link, admin_date
from orchestra.apps.accounts.admin import AccountAdminMixin

from . import settings
from .actions import generate_bill
from .filters import BillTypeListFilter
from .models import (Bill, Invoice, AmendmentInvoice, Fee, AmendmentFee, Budget,
        BillLine, BudgetLine)


class BillLineInline(admin.TabularInline):
    model = BillLine
    fields = ('description', 'rate', 'amount', 'tax', 'total', 'subtotal')
    readonly_fields = ('subtotal',)
    
    def subtotal(self, line):
        if line.total:
            subtotal = 0
            for subline in line.sublines.all():
                subtotal += subline.total
            return line.total - subtotal
        return ''
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != Bill.OPEN:
            return self.fields
        return super(BillLineInline, self).get_readonly_fields(request, obj=obj)
    
    def has_add_permission(self, request):
        if request.__bill__ and request.__bill__.status != Bill.OPEN:
            return False
        return super(BillLineInline, self).has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        if obj and obj.status != Bill.OPEN:
            return False
        return super(BillLineInline, self).has_delete_permission(request, obj=obj)


class BudgetLineInline(admin.TabularInline):
    model = Budget
    fields = ('description', 'rate', 'amount', 'tax', 'total')


class BillAdmin(AccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'number', 'status', 'type_link', 'account_link', 'created_on_display',
        'num_lines', 'display_total'
    )
    list_filter = (BillTypeListFilter, 'status',)
    add_fields = ('account', 'type', 'status', 'due_on', 'comments')
    fieldsets = (
        (None, {
            'fields': ('number', 'display_total', 'account_link', 'type',
                       'status', 'due_on', 'comments'),
        }),
        (_("Raw"), {
            'classes': ('collapse',),
            'fields': ('html',),
        }),
    )
    change_view_actions = [generate_bill]
    change_readonly_fields = ('account_link', 'type', 'status')
    readonly_fields = ('number', 'display_total')
    inlines = [BillLineInline]
    
    created_on_display = admin_date('created_on')
    
    def num_lines(self, bill):
        return bill.billlines__count
    num_lines.admin_order_field = 'billlines__count'
    num_lines.short_description = _("lines")
    
    def display_total(self, bill):
        return "%i &%s;" % (bill.get_total(), settings.BILLS_CURRENCY.lower())
    display_total.allow_tags = True
    display_total.short_description = _("total")
    
    def type_link(self, bill):
        bill_type = bill.type.lower()
        url = reverse('admin:bills_%s_changelist' % bill_type)
        return '<a href="%s">%s</a>' % (url, bill.get_type_display())
    type_link.allow_tags = True
    type_link.short_description = _("type")
    type_link.admin_order_field = 'type'
    
    def get_readonly_fields(self, request, obj=None):
        fields = super(BillAdmin, self).get_readonly_fields(request, obj=obj)
        if obj and obj.status != Bill.OPEN:
            fields += self.add_fields
        return fields
    
    def get_inline_instances(self, request, obj=None):
        if self.model is Budget:
            self.inlines = [BudgetLineInline]
        # Make parent object available for inline.has_add_permission()
        request.__bill__ = obj
        return super(BillAdmin, self).get_inline_instances(request, obj=obj)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'comments':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 4})
        if db_field.name == 'html':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 150, 'rows': 20})
        return super(BillAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        
    def queryset(self, request):
        qs = super(BillAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('billlines'))
        qs = qs.prefetch_related('billlines', 'billlines__sublines')
        return qs


admin.site.register(Bill, BillAdmin)
admin.site.register(Invoice, BillAdmin)
admin.site.register(AmendmentInvoice, BillAdmin)
admin.site.register(Fee, BillAdmin)
admin.site.register(AmendmentFee, BillAdmin)
admin.site.register(Budget, BillAdmin)
