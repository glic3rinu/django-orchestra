from django.contrib import admin

from orchestra.admin.utils import admin_colored, admin_link
from orchestra.apps.accounts.admin import AccountAdminMixin

from .methods import BankTransfer
from .models import PaymentSource, Transaction


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
    
    bill_link = admin_link('bill')
    account_link = admin_link('bill__account')
    display_state = admin_colored('state', colors=STATE_COLORS)


class PaymentSourceAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = ('label', 'method', 'number', 'account_link', 'is_active')
    list_filter = ('method', 'is_active')
    form = BankTransfer().get_form()
    # TODO select payment source method


admin.site.register(PaymentSource, PaymentSourceAdmin)
admin.site.register(Transaction, TransactionAdmin)
