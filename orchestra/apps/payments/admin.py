from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.utils import admin_colored, admin_link, wrap_admin_view
from orchestra.apps.accounts.admin import AccountAdminMixin

from .actions import process_transactions
from .methods import PaymentMethod
from .models import PaymentSource, Transaction, TransactionProcess


STATE_COLORS = {
    Transaction.WAITTING_PROCESSING: 'darkorange',
    Transaction.WAITTING_CONFIRMATION: 'magenta',
    Transaction.CONFIRMED: 'olive',
    Transaction.SECURED: 'green',
    Transaction.REJECTED: 'red',
    Transaction.DISCARTED: 'blue',
}


class TransactionInline(admin.TabularInline):
    model = Transaction
    can_delete = False
    extra = 0
    fields = ('transaction_link', 'bill_link', 'source_link', 'display_state', 'amount', 'currency')
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


class TransactionAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = (
        'id', 'bill_link', 'account_link', 'source_link', 'display_state', 'amount', 'process_link'
    )
    list_filter = ('source__method', 'state')
    actions = (process_transactions,)
    filter_by_account_fields = ['source']
    readonly_fields = ('process_link', 'account_link')
    
    bill_link = admin_link('bill')
    source_link = admin_link('source')
    process_link = admin_link('process', short_description=_("proc"))
    account_link = admin_link('bill__account')
    display_state = admin_colored('state', colors=STATE_COLORS)
    
    def get_queryset(self, request):
        qs = super(TransactionAdmin, self).get_queryset(request)
        return qs.select_related('source', 'bill__account__user')


class PaymentSourceAdmin(AccountAdminMixin, admin.ModelAdmin):
    list_display = ('label', 'method', 'number', 'account_link', 'is_active')
    list_filter = ('method', 'is_active')
    
    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = obj.method_class().get_form()
        else:
            self.form = PaymentMethod.get_plugin(self.method)().get_form()
        return super(PaymentSourceAdmin, self).get_form(request, obj=obj, **kwargs)
    
    def get_urls(self):
        """ Hooks select account url """
        urls = super(PaymentSourceAdmin, self).get_urls()
        admin_site = self.admin_site
        opts = self.model._meta
        info = opts.app_label, opts.model_name
        select_urls = patterns("",
            url("/select-method/$",
                wrap_admin_view(self, self.select_method_view),
                name='%s_%s_select_method' % info),
        )
        return select_urls + urls 
    
    def select_method_view(self, request):
        context = {
            'methods': PaymentMethod.get_plugin_choices(),
        }
        return render(request, 'admin/payments/payment_source/select_method.html', context)
    
    def add_view(self, request, form_url='', extra_context=None):
        """ Redirects to select account view if required """
        if request.user.is_superuser:
            method = request.GET.get('method')
            if method or PaymentMethod.get_plugins() == 1:
                self.method = method
                if not method:
                    self.method = PaymentMethod.get_plugins()[0]
                return super(PaymentSourceAdmin, self).add_view(request,
                        form_url=form_url, extra_context=extra_context)
        return redirect('./select-method/?%s' % request.META['QUERY_STRING'])
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.method = self.method
        obj.save()


class TransactionProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_url', 'display_transactions', 'created_at')
    fields = ('data', 'file_url', 'display_transactions', 'created_at')
    readonly_fields = ('file_url', 'display_transactions', 'created_at')
    inlines = [TransactionInline]
    
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
admin.site.register(TransactionProcess, TransactionProcessAdmin)
