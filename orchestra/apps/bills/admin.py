from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import admin_link, admin_date
from orchestra.apps.accounts.admin import AccountAdminMixin

from .actions import generate_bill
from .filters import BillTypeListFilter
from .models import (Bill, Invoice, AmendmentInvoice, Fee, AmendmentFee, Budget,
        BillLine, BudgetLine)


class BillLineInline(admin.TabularInline):
    model = BillLine
    fields = (
        'description', 'initial_date', 'final_date', 'price', 'amount', 'tax'
    )


class BudgetLineInline(admin.TabularInline):
    model = Budget
    fields = (
        'description', 'initial_date', 'final_date', 'price', 'amount', 'tax'
    )


class BillAdmin(AccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'ident', 'status', 'type_link', 'account_link', 'created_on_display'
    )
    list_filter = (BillTypeListFilter, 'status',)
    change_view_actions = [generate_bill]
    change_readonly_fields = ('account', 'type', 'status')
    readonly_fields = ('ident',)
    inlines = [BillLineInline]
    
    account_link = admin_link('account')
    created_on_display = admin_date('created_on')
    
    def type_link(self, bill):
        bill_type = bill.type.lower()
        url = reverse('admin:bills_%s_changelist' % bill_type)
        return '<a href="%s">%s</a>' % (url, bill.get_type_display())
    type_link.allow_tags = True
    type_link.short_description = _("type")
    type_link.admin_order_field = 'type'
    
    def get_inline_instances(self, request, obj=None):
        if self.model is Budget:
            self.inlines = [BudgetLineInline]
        return super(BillAdmin, self).get_inline_instances(request, obj=obj)


admin.site.register(Bill, BillAdmin)
admin.site.register(Invoice, BillAdmin)
admin.site.register(AmendmentInvoice, BillAdmin)
admin.site.register(Fee, BillAdmin)
admin.site.register(AmendmentFee, BillAdmin)
admin.site.register(Budget, BillAdmin)
