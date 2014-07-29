from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import admin_colored, admin_link
from orchestra.apps.accounts.admin import AccountAdminMixin

from .actions import process_transactions
from .methods import BankTransfer
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


class PaymentSourceAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = ('label', 'method', 'number', 'account_link', 'is_active')
    list_filter = ('method', 'is_active')
    form = BankTransfer().get_form()
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
        links = []
        for transaction in process.transactions.all():
            url = reverse('admin:payments_transaction_change', args=(transaction.pk,))
            links.append(
                '<a href="%s">%s</a>' % (url, str(transaction))
            )
        return '<br>'.join(links)
    display_transactions.short_description = _("Transactions")
    display_transactions.allow_tags = True


admin.site.register(PaymentSource, PaymentSourceAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(PaymentProcess, PaymentProcessAdmin)
