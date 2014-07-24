from django.contrib import admin

from orchestra.admin.utils import admin_colored, admin_link

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
        'id', 'bill_link', 'account_link', 'method', 'display_state', 'amount'
    )
    list_filter = ('method', 'state')
    
    bill_link = admin_link('bill')
    account_link = admin_link('bill__account')
    display_state = admin_colored('state', colors=STATE_COLORS)


admin.site.register(PaymentSource)
admin.site.register(Transaction, TransactionAdmin)
