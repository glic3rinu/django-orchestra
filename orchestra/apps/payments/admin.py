from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ChangeViewActionsMixin, SelectPluginAdminMixin
from orchestra.admin.utils import admin_colored, admin_link
from orchestra.apps.accounts.admin import AccountAdminMixin

from . import actions
from .methods import PaymentMethod
from .models import PaymentSource, Transaction, TransactionProcess


STATE_COLORS = {
    Transaction.WAITTING_PROCESSING: 'darkorange',
    Transaction.WAITTING_EXECUTION: 'magenta',
    Transaction.EXECUTED: 'olive',
    Transaction.SECURED: 'green',
    Transaction.REJECTED: 'red',
}


class PaymentSourceAdmin(SelectPluginAdminMixin, AccountAdminMixin, admin.ModelAdmin):
    list_display = ('label', 'method', 'number', 'account_link', 'is_active')
    list_filter = ('method', 'is_active')
    plugin = PaymentMethod
    plugin_field = 'method'


class TransactionInline(admin.TabularInline):
    model = Transaction
    can_delete = False
    extra = 0
    fields = (
        'transaction_link', 'bill_link', 'source_link', 'display_state',
        'amount', 'currency'
    )
    readonly_fields = fields
    
    transaction_link = admin_link('__unicode__', short_description=_("ID"))
    bill_link = admin_link('bill')
    source_link = admin_link('source')
    display_state = admin_colored('state', colors=STATE_COLORS)
    
    class Media:
        css = {
            'all': ('orchestra/css/hide-inline-id.css',)
        }
    
    def has_add_permission(self, *args, **kwargs):
        return False


class TransactionAdmin(ChangeViewActionsMixin, AccountAdminMixin, admin.ModelAdmin):
    list_display = (
        'id', 'bill_link', 'account_link', 'source_link', 'display_state',
        'amount', 'process_link'
    )
    list_filter = ('source__method', 'state')
    actions = (
        actions.process_transactions, actions.mark_as_executed,
        actions.mark_as_secured, actions.mark_as_rejected
    )
    change_view_actions = actions
    filter_by_account_fields = ['source']
    readonly_fields = ('bill_link', 'display_state', 'process_link', 'account_link')
    
    bill_link = admin_link('bill')
    source_link = admin_link('source')
    process_link = admin_link('process', short_description=_("proc"))
    account_link = admin_link('bill__account')
    display_state = admin_colored('state', colors=STATE_COLORS)
    
    def get_queryset(self, request):
        qs = super(TransactionAdmin, self).get_queryset(request)
        return qs.select_related('source', 'bill__account')
    
    def get_change_view_actions(self, obj=None):
        actions = super(TransactionAdmin, self).get_change_view_actions()
        exclude = []
        if obj:
            if obj.state == Transaction.WAITTING_PROCESSING:
                exclude = ['mark_as_executed', 'mark_as_secured', 'mark_as_rejected']
            elif obj.state == Transaction.WAITTING_EXECUTION:
                exclude = ['process_transactions', 'mark_as_secured', 'mark_as_rejected']
            if obj.state == Transaction.EXECUTED:
                exclude = ['process_transactions', 'mark_as_executed']
            elif obj.state in [Transaction.REJECTED, Transaction.SECURED]:
                return []
        return [action for action in actions if action.__name__ not in exclude]


class TransactionProcessAdmin(ChangeViewActionsMixin, admin.ModelAdmin):
    list_display = ('id', 'file_url', 'display_transactions', 'created_at')
    fields = ('data', 'file_url', 'display_transactions', 'created_at')
    readonly_fields = ('file_url', 'display_transactions', 'created_at')
    inlines = [TransactionInline]
    actions = (actions.mark_process_as_executed, actions.abort, actions.commit)
    change_view_actions = actions
    
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
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def get_change_view_actions(self, obj=None):
        actions = super(TransactionProcessAdmin, self).get_change_view_actions()
        exclude = []
        if obj:
            if obj.state == TransactionProcess.EXECUTED:
                exclude.append('mark_process_as_executed')
            elif obj.state == TransactionProcess.COMMITED:
                exclude = ['mark_process_as_executed', 'abort', 'commit']
            elif obj.state == TransactionProcess.ABORTED:
                exclude = ['mark_process_as_executed', 'abort', 'commit']
        return [action for action in actions if action.__name__ not in exclude]


admin.site.register(PaymentSource, PaymentSourceAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionProcess, TransactionProcessAdmin)
