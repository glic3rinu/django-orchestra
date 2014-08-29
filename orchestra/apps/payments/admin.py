from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import admin_colored, admin_link
from orchestra.apps.accounts.admin import AccountAdminMixin

from .actions import process_transactions
from .methods import SEPADirectDebit
from .models import PaymentSource, Transaction, PaymentProcess


STATE_COLORS = {
    Transaction.WAITTING_PROCESSING: 'darkorange',
    Transaction.WAITTING_CONFIRMATION: 'orange',
    Transaction.CONFIRMED: 'green',
    Transaction.REJECTED: 'red',
    Transaction.LOCKED: 'magenta',
    Transaction.DISCARTED: 'blue',
}


class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'bill_link', 'account_link', 'source', 'display_state', 'amount'
    )
    list_filter = ('source__method', 'state')
    actions = (process_transactions,)
    
    bill_link = admin_link('bill')
    account_link = admin_link('bill__account')
    display_state = admin_colored('state', colors=STATE_COLORS)
    
    def get_queryset(self, request):
        qs = super(TransactionAdmin, self).get_queryset(request)
        return qs.select_related('source', 'bill__account__user')


class PaymentSourceAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = ('label', 'method', 'number', 'account_link', 'is_active')
    list_filter = ('method', 'is_active')
    form = SEPADirectDebit().get_form()
    # TODO select payment source method


class PaymentProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_url', 'display_transactions', 'created_at')
    fields = ('data', 'file_url', 'display_transactions', 'created_at')
    readonly_fields = ('file_url', 'display_transactions', 'created_at')
    
    def file_url(self, process):
        if process.file:
            return '<a href="%s">%s</a>' % (process.file.url, process.file.name)
    file_url.allow_tags = True
    file_url.admin_order_field = 'file'
    
    def display_transactions(self, process):
        ids = []
        lines = []
        counter = 0
        # Because of values_list this query doesn't benefit from prefetch_related
        tx_ids = process.transactions.values_list('id', flat=True)
        for tx_id in tx_ids:
            ids.append(str(tx_id))
            counter += 1
            if counter > 10:
                counter = 0
                lines.append(','.join(ids))
                ids = []
        lines.append(','.join(ids))
        url = reverse('admin:payments_transaction_changelist')
        url += '?processes=%i' % process.id
        return '<a href="%s">%s</a>' % (url, '<br>'.join(lines))
    display_transactions.short_description = _("Transactions")
    display_transactions.allow_tags = True


admin.site.register(PaymentSource, PaymentSourceAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(PaymentProcess, PaymentProcessAdmin)
