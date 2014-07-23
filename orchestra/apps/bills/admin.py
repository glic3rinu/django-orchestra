from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import admin_link, admin_date
from orchestra.apps.accounts.admin import AccountAdminMixin

from .filters import BillTypeListFilter
from .models import (Bill, Invoice, AmendmentInvoice, Fee, AmendmentFee, Budget,
        BillLine, BudgetLine)


class BillLineInline(admin.TabularInline):
    model = BillLine

class BudgetLineInline(admin.TabularInline):
    model = Budget


class BillAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = (
        'ident', 'status', 'bill_type_link', 'account_link', 'created_on_display'
    )
    list_filter = (BillTypeListFilter, 'status',)
    readonly_fields = ('ident',)
    inlines = [BillLineInline]
    
    account_link = admin_link('account')
    created_on_display = admin_date('created_on')
    
    def bill_type_link(self, bill):
        bill_type = bill.bill_type.lower()
        url = reverse('admin:bills_%s_changelist' % bill_type)
        return '<a href="%s">%s</a>' % (url, bill.get_bill_type_display())
    bill_type_link.allow_tags = True
    bill_type_link.short_description = _("type")
    bill_type_link.admin_order_field = 'bill_type'
    
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
