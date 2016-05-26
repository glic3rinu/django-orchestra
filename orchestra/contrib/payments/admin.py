from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ChangeViewActionsMixin, ExtendedModelAdmin
from orchestra.admin.utils import admin_colored, admin_link, admin_date
from orchestra.contrib.accounts.actions import list_accounts
from orchestra.contrib.accounts.admin import AccountAdminMixin, SelectAccountAdminMixin
from orchestra.plugins.admin import SelectPluginAdminMixin

from . import actions, helpers
from .methods import PaymentMethod
from .models import PaymentSource, Transaction, TransactionProcess


STATE_COLORS = {
    Transaction.WAITTING_PROCESSING: 'darkorange',
    Transaction.WAITTING_EXECUTION: 'magenta',
    Transaction.EXECUTED: 'olive',
    Transaction.SECURED: 'green',
    Transaction.REJECTED: 'red',
}

PROCESS_STATE_COLORS = {
    TransactionProcess.CREATED: 'blue',
    TransactionProcess.EXECUTED: 'olive',
    TransactionProcess.ABORTED: 'red',
    TransactionProcess.COMMITED: 'green',
}


class PaymentSourceAdmin(SelectPluginAdminMixin, AccountAdminMixin, ExtendedModelAdmin):
    list_display = ('label', 'method', 'number', 'account_link', 'is_active')
    list_filter = ('method', 'is_active')
    change_readonly_fields = ('method',)
    search_fields = ('account__username', 'account__full_name', 'data')
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
    
    transaction_link = admin_link('__str__', short_description=_("ID"))
    bill_link = admin_link('bill')
    source_link = admin_link('source')
    display_state = admin_colored('state', colors=STATE_COLORS)
    
    class Media:
        css = {
            'all': ('orchestra/css/hide-inline-id.css',)
        }
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.select_related('source', 'bill')


class TransactionAdmin(SelectAccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'id', 'bill_link', 'account_link', 'source_link', 'display_created_at',
        'display_modified_at', 'display_state', 'amount', 'process_link'
    )
    list_filter = ('source__method', 'state')
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'account_link',
                'bill_link',
                'source_link',
                'display_state',
                'amount',
                'currency',
                'process_link'
            )
        }),
        (_("Dates"), {
            'classes': ('wide',),
            'fields': ('display_created_at', 'display_modified_at'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'bill',
                'source',
                'display_state',
                'amount',
                'currency',
            )
        }),
    )
    change_view_actions = (
        actions.process_transactions, actions.mark_as_executed, actions.mark_as_secured,
        actions.mark_as_rejected, actions.reissue
    )
    search_fields = ('bill__number', 'bill__account__username', 'id')
    actions = change_view_actions + (actions.report, list_accounts,)
    filter_by_account_fields = ('bill', 'source')
    readonly_fields = (
        'bill_link', 'display_state', 'process_link', 'account_link', 'source_link',
        'display_created_at', 'display_modified_at'
    )
    list_select_related = ('source', 'bill__account', 'process')
    date_hierarchy = 'created_at'
    
    bill_link = admin_link('bill')
    source_link = admin_link('source')
    process_link = admin_link('process', short_description=_("proc"))
    account_link = admin_link('bill__account')
    display_created_at = admin_date('created_at', short_description=_("Created"))
    display_modified_at = admin_date('modified_at', short_description=_("Modified"))
    
    def has_delete_permission(self, *args, **kwargs):
        return False
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    def get_change_readonly_fields(self, request, obj):
        if obj.state in (Transaction.WAITTING_PROCESSING, Transaction.WAITTING_EXECUTION):
            return ()
        return ('amount', 'currency')
    
    def get_change_view_actions(self, obj=None):
        actions = super(TransactionAdmin, self).get_change_view_actions()
        exclude = []
        if obj:
            if obj.state == Transaction.WAITTING_PROCESSING:
                exclude = ['mark_as_executed', 'mark_as_secured', 'reissue']
            elif obj.state == Transaction.WAITTING_EXECUTION:
                exclude = ['process_transactions', 'mark_as_secured', 'reissue']
            if obj.state == Transaction.EXECUTED:
                exclude = ['process_transactions', 'mark_as_executed', 'reissue']
            elif obj.state == Transaction.REJECTED:
                exclude = ['process_transactions', 'mark_as_executed', 'mark_as_secured', 'mark_as_rejected']
            elif obj.state == Transaction.SECURED:
                return []
        return [action for action in actions if action.__name__ not in exclude]
    
    def display_state(self, obj):
        state = admin_colored('state', colors=STATE_COLORS)(obj)
        help_text = obj.get_state_help()
        state = state.replace('<span ', '<span title="%s" ' % help_text)
        return state
    display_state.admin_order_field = 'state'
    display_state.short_description = _("State")
    display_state.allow_tags = True


class TransactionProcessAdmin(ChangeViewActionsMixin, admin.ModelAdmin):
    list_display = (
        'id', 'file_url', 'display_transactions', 'display_state', 'display_created_at',
    )
    list_filter = ('state',)
    fields = ('data', 'file_url', 'created_at')
    search_fields = ('transactions__bill__number', 'transactions__bill__account__username', 'id')
    readonly_fields = ('data', 'file_url', 'display_transactions', 'created_at')
    list_prefetch_related = ('transactions',)
    inlines = [TransactionInline]
    change_view_actions = (
        actions.mark_process_as_executed, actions.abort, actions.commit, actions.report
    )
    actions = change_view_actions + (actions.delete_selected,)
    
    display_state = admin_colored('state', colors=PROCESS_STATE_COLORS)
    display_created_at = admin_date('created_at', short_description=_("Created"))
    
    def file_url(self, process):
        if process.file:
            return '<a href="%s">%s</a>' % (process.file.url, process.file.name)
    file_url.allow_tags = True
    file_url.admin_order_field = 'file'
    
    def display_transactions(self, process):
        ids = []
        lines = []
        counter = 0
        for trans in process.transactions.all():
            color = STATE_COLORS.get(trans.state, 'black')
            state = trans.get_state_display()
            ids.append('<span style="color:%s" title="%s">%i</span>' % (color, state, trans.id))
            counter += 1 + len(str(trans.id))
            if counter > 100:
                counter = 0
                lines.append(','.join(ids))
                ids = []
        lines.append(','.join(ids))
        transactions = '<br>'.join(lines)
        url = reverse('admin:payments_transaction_changelist')
        url += '?process_id=%i' % process.id
        return '<a href="%s">%s</a>' % (url, transactions)
    display_transactions.short_description = _("Transactions")
    display_transactions.allow_tags = True
    
    def has_add_permission(self, *args, **kwargs):
        return False
    
    def get_change_view_actions(self, obj=None):
        actions = super().get_change_view_actions()
        exclude = []
        if obj:
            if obj.state == TransactionProcess.EXECUTED:
                exclude.append('mark_process_as_executed')
            elif obj.state == TransactionProcess.COMMITED:
                exclude = ['mark_process_as_executed', 'abort', 'commit']
            elif obj.state == TransactionProcess.ABORTED:
                exclude = ['mark_process_as_executed', 'abort', 'commit']
        return [action for action in actions if action.__name__ not in exclude]
    
    def delete_view(self, request, object_id, extra_context=None):
        queryset = self.model.objects.filter(id=object_id)
        related_transactions = helpers.pre_delete_processes(self, request, queryset)
        response = super().delete_view(request, object_id, extra_context)
        if isinstance(response, HttpResponseRedirect):
            helpers.post_delete_processes(self, request, related_transactions)
        return response

admin.site.register(PaymentSource, PaymentSourceAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionProcess, TransactionProcessAdmin)
