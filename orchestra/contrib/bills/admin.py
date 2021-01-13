from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F, Sum, Prefetch
from django.db.models.functions import Coalesce
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import admin_date, insertattr, admin_link, change_url
from orchestra.contrib.accounts.actions import list_accounts
from orchestra.contrib.accounts.admin import AccountAdminMixin, AccountAdmin
from orchestra.forms.widgets import paddingCheckboxSelectMultiple

from . import settings, actions
from .filters import (BillTypeListFilter, HasBillContactListFilter, TotalListFilter,
    PaymentStateListFilter, AmendedListFilter)
from .models import (Bill, Invoice, AmendmentInvoice, AbonoInvoice, Fee, AmendmentFee, ProForma, BillLine,
    BillSubline, BillContact)


PAYMENT_STATE_COLORS = {
    Bill.OPEN: 'grey',
    Bill.CREATED: 'magenta',
    Bill.PROCESSED: 'darkorange',
    Bill.AMENDED: 'blue',
    Bill.PAID: 'green',
    Bill.EXECUTED: 'olive',
    Bill.BAD_DEBT: 'red',
    Bill.INCOMPLETE: 'red',
}


class BillSublineInline(admin.TabularInline):
    model = BillSubline
    fields = ('description', 'total', 'type')
    
    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj and not obj.bill.is_open:
            return self.get_fields(request)
        return fields
    
    def get_max_num(self, request, obj=None):
        if obj and not obj.bill.is_open:
            return 0
        return super().get_max_num(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        if obj and not obj.bill.is_open:
            return False
        return super().has_delete_permission(request, obj)


class BillLineInline(admin.TabularInline):
    model = BillLine
    fields = (
        'description', 'order_link', 'start_on', 'end_on', 'rate', 'quantity', 'tax',
        'subtotal', 'display_total',
    )
    readonly_fields = ('display_total', 'order_link')
    
    order_link = admin_link('order', display='pk')
    
    def display_total(self, line):
        if line.pk:
            total = line.compute_total()
            sublines = line.sublines.all()
            url = change_url(line)
            if sublines:
                content = '\n'.join(['%s: %s' % (sub.description, sub.total) for sub in sublines])
                img = static('admin/img/icon-alert.svg')
                return '<a href="%s" title="%s">%s <img src="%s"></img></a>' % (url, content, total, img)
            return '<a href="%s">%s</a>' % (url, total)
    display_total.short_description = _("Total")
    display_total.allow_tags = True
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'description':
            kwargs['widget'] = forms.TextInput(attrs={'size':'50'})
        elif db_field.name not in ('start_on', 'end_on'):
            kwargs['widget'] = forms.TextInput(attrs={'size':'6'})
        return super().formfield_for_dbfield(db_field, **kwargs)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('sublines').select_related('order')


class ClosedBillLineInline(BillLineInline):
    # TODO reimplement as nested inlines when upstream
    #      https://code.djangoproject.com/ticket/9025
    
    fields = (
        'display_description', 'order_link', 'start_on', 'end_on', 'rate', 'quantity', 'tax',
        'display_subtotal', 'display_total'
    )
    readonly_fields = fields
    can_delete = False
    
    def display_description(self, line):
        descriptions = [line.description]
        for subline in line.sublines.all():
            descriptions.append('&nbsp;'*4+subline.description)
        return '<br>'.join(descriptions)
    display_description.short_description = _("Description")
    display_description.allow_tags = True
    
    def display_subtotal(self, line):
        subtotals = ['&nbsp;' + str(line.subtotal)]
        for subline in line.sublines.all():
            subtotals.append(str(subline.total))
        return '<br>'.join(subtotals)
    display_subtotal.short_description = _("Subtotal")
    display_subtotal.allow_tags = True
    
    def display_total(self, line):
        if line.pk:
            return line.compute_total()
    display_total.short_description = _("Total")
    display_total.allow_tags = True
    
    def has_add_permission(self, request):
        return False


class BillLineAdmin(admin.ModelAdmin):
    list_display = (
        'description', 'bill_link', 'display_is_open', 'account_link', 'rate', 'quantity',
        'tax', 'subtotal', 'display_sublinetotal', 'display_total'
    )
    actions = (
        actions.undo_billing, actions.move_lines, actions.copy_lines, actions.service_report,
        actions.list_bills,
    )
    fieldsets = (
        (None, {
            'fields': ('bill_link', 'description', 'tax', 'start_on', 'end_on', 'amended_line_link')
        }),
        (_("Totals"), {
            'fields': ('rate', ('quantity', 'verbose_quantity'), 'subtotal', 'display_sublinetotal',
                       'display_total'),
        }),
        (_("Order"), {
            'fields': ('order_link', 'order_billed_on', 'order_billed_until',)
        }),
    )
    readonly_fields = (
        'bill_link', 'order_link', 'amended_line_link', 'display_sublinetotal', 'display_total'
    )
    list_filter = ('tax', 'bill__is_open', 'order__service')
    list_select_related = ('bill', 'bill__account')
    search_fields = ('description', 'bill__number')
    inlines = (BillSublineInline,)
    
    account_link = admin_link('bill__account')
    bill_link = admin_link('bill')
    order_link = admin_link('order')
    amended_line_link = admin_link('amended_line')
    
    def display_is_open(self, instance):
        return instance.bill.is_open
    display_is_open.short_description = _("Is open")
    display_is_open.boolean = True
    
    def display_sublinetotal(self, instance):
        total = instance.subline_total
        return total if total is not None else '---'
    display_sublinetotal.short_description = _("Sublines")
    display_sublinetotal.admin_order_field = 'subline_total'
    
    def display_total(self, instance):
        return round(instance.computed_total or 0, 2)
    display_total.short_description = _("Total")
    display_total.admin_order_field = 'computed_total'
    
    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj and not obj.bill.is_open:
            return list(fields) + [
                'description', 'tax', 'start_on', 'end_on', 'rate', 'quantity', 'verbose_quantity',
                'subtotal', 'order_billed_on', 'order_billed_until'
            ]
        return fields
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            subline_total=Sum('sublines__total'),
            computed_total=(F('subtotal') + Sum(Coalesce('sublines__total', 0))) * (1+F('tax')/100),
        )
        return qs
    
    def has_delete_permission(self, request, obj=None):
        if obj and not obj.bill.is_open:
            return False
        return super().has_delete_permission(request, obj)


class BillLineManagerAdmin(BillLineAdmin):
    def get_queryset(self, request):
        qset = super().get_queryset(request)
        if self.bill_ids:
            return qset.filter(bill_id__in=self.bill_ids)
        return qset
    
    def changelist_view(self, request, extra_context=None):
        GET_copy = request.GET.copy()
        bill_ids = GET_copy.pop('ids', None)
        if bill_ids:
            bill_ids = bill_ids[0]
            request.GET = GET_copy
            bill_ids = list(map(int, bill_ids.split(',')))
        else:
            messages.error(request, _("No bills selected."))
            return redirect('..')
        self.bill_ids = bill_ids
        bill = None
        if len(bill_ids) == 1:
            bill_url = reverse('admin:bills_bill_change', args=(bill_ids[0],))
            bill = Bill.objects.get(pk=bill_ids[0])
            bill_link = '<a href="%s">%s</a>' % (bill_url, bill.number)
            title = mark_safe(_("Manage %s bill lines") % bill_link)
            if not bill.is_open:
                messages.warning(request, _("Bill not in open state."))
        else:
            if Bill.objects.filter(id__in=bill_ids, is_open=False).exists():
                messages.warning(request, _("Not all bills are in open state."))
            title = _("Manage bill lines of multiple bills")
        context = {
            'title': title,
            'bill': bill,
        }
        context.update(extra_context or {})
        return super().changelist_view(request, context)


class BillAdminMixin(AccountAdminMixin):
    def display_total_with_subtotals(self, bill):
        if bill.pk:
            currency = settings.BILLS_CURRENCY.lower()
            subtotals = []
            for tax, subtotal in bill.compute_subtotals().items():
                subtotals.append(_("Subtotal %s%% VAT   %s &%s;") % (tax, subtotal[0], currency))
                subtotals.append(_("Taxes %s%% VAT   %s &%s;") % (tax, subtotal[1], currency))
            subtotals = '\n'.join(subtotals)
            return '<span title="%s">%s &%s;</span>' % (subtotals, bill.compute_total(), currency)
    display_total_with_subtotals.allow_tags = True
    display_total_with_subtotals.short_description = _("total")
    display_total_with_subtotals.admin_order_field = 'approx_total'

    def display_payment_state(self, bill):
        if bill.pk:
            t_opts = bill.transactions.model._meta
            if bill.get_type() == bill.PROFORMA:
                return '<span title="Pro forma">---</span>'
            transactions = bill.transactions.all()
            if len(transactions) == 1:
                args = (transactions[0].pk,)
                view = 'admin:%s_%s_change' % (t_opts.app_label, t_opts.model_name)
                url = reverse(view, args=args)
            else:
                url = reverse('admin:%s_%s_changelist' % (t_opts.app_label, t_opts.model_name))
                url += '?bill=%i' % bill.pk
            state = bill.get_payment_state_display().upper()
            title = ''
            if bill.closed_amends:
                state = '<strike>%s*</strike>' % state
                title = _("This bill has been amended, this value may not be valid.")
            color = PAYMENT_STATE_COLORS.get(bill.payment_state, 'grey')
            return '<a href="{url}" style="color:{color}" title="{title}">{name}</a>'.format(
                url=url, color=color, name=state, title=title)
    display_payment_state.allow_tags = True
    display_payment_state.short_description = _("Payment")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            models.Count('lines'),
            # FIXME https://code.djangoproject.com/ticket/10060
            approx_total=Coalesce(Sum(
                (F('lines__subtotal') + Coalesce('lines__sublines__total', 0)) * (1+F('lines__tax')/100),
            ), 0),
        )
        qs = qs.prefetch_related(
            Prefetch('amends', queryset=Bill.objects.filter(is_open=False), to_attr='closed_amends')
        )
        return qs.defer('html')


class AmendInline(BillAdminMixin, admin.TabularInline):
    model = Bill
    fields = (
        'self_link', 'type', 'display_total_with_subtotals', 'display_payment_state', 'is_open',
        'is_sent'
    )
    readonly_fields = fields
    verbose_name_plural = _("Amends")
    can_delete = False
    extra = 0
    
    self_link = admin_link('__str__')
    
    def has_add_permission(self, *args, **kwargs):
        return False


class BillAdmin(BillAdminMixin, ExtendedModelAdmin):
    list_display = (
        'number', 'type_link', 'account_link', 'closed_on_display', 'updated_on_display',
        'num_lines', 'display_total', 'display_payment_state', 'is_sent'
    )
    list_filter = (
        BillTypeListFilter, 'is_open', 'is_sent', TotalListFilter, PaymentStateListFilter,
        AmendedListFilter, 'account__is_active',
    )
    add_fields = ('account', 'type', 'amend_of', 'is_open', 'due_on', 'comments')
    change_list_template = 'admin/bills/bill/change_list.html'
    fieldsets = (
        (None, {
            'fields': ['number', 'type', (), 'account_link', 'display_total_with_subtotals',
                       'display_payment_state', 'is_sent', 'comments'],
        }),
        (_("Dates"), {
            'classes': ('collapse',),
            'fields': ('created_on_display', 'closed_on_display', 'updated_on_display',
                       'due_on'),
        }),
        (_("Raw"), {
            'classes': ('collapse',),
            'fields': ('html',),
        }),
    )
    list_prefetch_related = ('transactions', 'lines__sublines')
    search_fields = ('number', 'account__username', 'comments')
    change_view_actions = [
        actions.manage_lines, actions.view_bill, actions.download_bills, actions.send_bills,
        actions.close_bills, actions.amend_bills, actions.close_send_download_bills,
    ]
    actions = [
        actions.manage_lines, actions.download_bills, actions.close_bills, actions.send_bills,
        actions.amend_bills, actions.bill_report, actions.service_report,
        actions.close_send_download_bills, list_accounts,
    ]
    change_readonly_fields = ('account_link', 'type', 'is_open', 'amend_of_link')
    readonly_fields = (
        'number', 'display_total', 'is_sent', 'display_payment_state', 'created_on_display',
        'closed_on_display', 'updated_on_display', 'display_total_with_subtotals',
    )
    date_hierarchy = 'closed_on'
    
    created_on_display = admin_date('created_on', short_description=_("Created"))
    closed_on_display = admin_date('closed_on', short_description=_("Closed"))
    updated_on_display = admin_date('updated_on', short_description=_("Updated"))
    amend_of_link = admin_link('amend_of')
    
#    def amend_links(self, bill):
#        links = []
#        for amend in bill.amends.all():
#            url = reverse('admin:bills_bill_change', args=(amend.id,))
#            links.append('<a href="{url}">{num}</a>'.format(url=url, num=amend.number))
#        return '<br>'.join(links)
#    amend_links.short_description = _("Amends")
#    amend_links.allow_tags = True
    
    def num_lines(self, bill):
        return bill.lines__count
    num_lines.admin_order_field = 'lines__count'
    num_lines.short_description = _("lines")
    
    def display_total(self, bill):
        currency = settings.BILLS_CURRENCY.lower()
        return '%s &%s;' % (bill.compute_total(), currency)
    display_total.allow_tags = True
    display_total.short_description = _("total")
    display_total.admin_order_field = 'approx_total'
    
    def type_link(self, bill):
        bill_type = bill.type.lower()
        url = reverse('admin:bills_%s_changelist' % bill_type)
        return '<a href="%s">%s</a>' % (url, bill.get_type_display())
    type_link.allow_tags = True
    type_link.short_description = _("type")
    type_link.admin_order_field = 'type'
    
    def get_urls(self):
        """ Hook bill lines management URLs on bill admin """
        urls = super().get_urls()
        admin_site = self.admin_site
        extra_urls = [
            url("^manage-lines/$",
                admin_site.admin_view(BillLineManagerAdmin(BillLine, admin_site).changelist_view),
                name='bills_bill_manage_lines'),
        ]
        return extra_urls + urls
    
    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj and not obj.is_open:
            fields += self.add_fields
        return fields
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:
            # Switches between amend_of_link and amend_links fields
            fields = fieldsets[0][1]['fields']
            if obj.amend_of_id:
                fields[2] = 'amend_of_link'
            else:
                fields[2] = ()
            if obj.is_open:
                fieldsets = fieldsets[0:-1]
        return fieldsets
    
    def get_change_view_actions(self, obj=None):
        actions = super().get_change_view_actions(obj)
        exclude = []
        if obj:
            if not obj.is_open:
                exclude += ['close_bills', 'close_send_download_bills']
            if obj.type not in obj.AMEND_MAP:
                exclude += ['amend_bills']
        return [action for action in actions if action.__name__ not in exclude]
    
    def get_inline_instances(self, request, obj=None):
        cls = type(self)
        if obj and not obj.is_open:
            if obj.amends.all():
                cls.inlines = [AmendInline, ClosedBillLineInline]
            else:
                cls.inlines = [ClosedBillLineInline]
        else:
            cls.inlines = [BillLineInline]
        return super().get_inline_instances(request, obj)
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'comments':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 4})
        elif db_field.name == 'html':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 150, 'rows': 20})
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'amend_of':
            formfield.queryset = formfield.queryset.filter(is_open=False)
        return formfield
    
    def change_view(self, request, object_id, **kwargs):
        # TODO raise404, here and everywhere
        bill = self.get_object(request, unquote(object_id))
        actions.validate_contact(request, bill, error=False)
        return super().change_view(request, object_id, **kwargs)


admin.site.register(Bill, BillAdmin)
admin.site.register(Invoice, BillAdmin)
admin.site.register(AmendmentInvoice, BillAdmin)
admin.site.register(AbonoInvoice, BillAdmin)
admin.site.register(Fee, BillAdmin)
admin.site.register(AmendmentFee, BillAdmin)
admin.site.register(ProForma, BillAdmin)
admin.site.register(BillLine, BillLineAdmin)


class BillContactInline(admin.StackedInline):
    model = BillContact
    fields = ('name', 'address', ('city', 'zipcode'), 'country', 'vat')
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'name':
            kwargs['widget'] = forms.TextInput(attrs={'size':'90'})
        if db_field.name == 'address':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 2})
        if db_field.name == 'email_usage':
            kwargs['widget'] = paddingCheckboxSelectMultiple(45)
        return super().formfield_for_dbfield(db_field, **kwargs)


def has_bill_contact(account):
    return hasattr(account, 'billcontact')
has_bill_contact.boolean = True
has_bill_contact.admin_order_field = 'billcontact'


insertattr(AccountAdmin, 'inlines', BillContactInline)
insertattr(AccountAdmin, 'list_display', has_bill_contact)
insertattr(AccountAdmin, 'list_filter', HasBillContactListFilter)
insertattr(AccountAdmin, 'list_select_related', 'billcontact')
