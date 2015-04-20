from django import forms
from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from orchestra.admin import ExtendedModelAdmin
from orchestra.admin.utils import admin_date, insertattr, admin_link
from orchestra.contrib.accounts.admin import AccountAdminMixin, AccountAdmin
from orchestra.forms.widgets import paddingCheckboxSelectMultiple

from . import settings, actions
from .filters import BillTypeListFilter, HasBillContactListFilter
from .models import Bill, Invoice, AmendmentInvoice, Fee, AmendmentFee, ProForma, BillLine, BillContact


PAYMENT_STATE_COLORS = {
    Bill.PAID: 'green',
    Bill.PENDING: 'darkorange',
    Bill.BAD_DEBT: 'red',
}


class BillLineInline(admin.TabularInline):
    model = BillLine
    fields = (
        'description', 'order_link', 'start_on', 'end_on', 'rate', 'quantity', 'tax',
        'subtotal', 'display_total',
    )
    readonly_fields = ('display_total', 'order_link')
    
    order_link = admin_link('order', display='pk')
    
    def display_total(self, line):
        total = line.get_total()
        sublines = line.sublines.all()
        if sublines:
            content = '\n'.join(['%s: %s' % (sub.description, sub.total) for sub in sublines])
            img = static('admin/img/icon_alert.gif')
            return '<span title="%s">%s <img src="%s"></img></span>' % (content, str(total), img)
        return total
    display_total.short_description = _("Total")
    display_total.allow_tags = True
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'description':
            kwargs['widget'] = forms.TextInput(attrs={'size':'50'})
        elif db_field.name not in ('start_on', 'end_on'):
            kwargs['widget'] = forms.TextInput(attrs={'size':'6'})
        return super(BillLineInline, self).formfield_for_dbfield(db_field, **kwargs)
    
    def get_queryset(self, request):
        qs = super(BillLineInline, self).get_queryset(request)
        return qs.prefetch_related('sublines')


class ClosedBillLineInline(BillLineInline):
    # TODO reimplement as nested inlines when upstream
    #      https://code.djangoproject.com/ticket/9025
    
    fields = (
        'display_description', 'order_link', 'start_on', 'end_on', 'rate', 'quantity', 'tax',
        'display_subtotal', 'display_total'
    )
    readonly_fields = fields
    
    def display_description(self, line):
        descriptions = [line.description]
        for subline in line.sublines.all():
            descriptions.append('&nbsp;'*4+subline.description)
        return '<br>'.join(descriptions)
    display_description.short_description = _("Description")
    display_description.allow_tags = True
    
    def display_subtotal(self, line):
        subtotals = ['&nbsp;&nbsp;' + str(line.subtotal)]
        for subline in line.sublines.all():
            subtotals.append(str(subline.total))
        return '<br>'.join(subtotals)
    display_subtotal.short_description = _("Subtotal")
    display_subtotal.allow_tags = True
    
    def display_total(self, line):
        return line.get_total()
    display_total.short_description = _("Total")
    display_total.allow_tags = True
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class BillLineManagerAdmin(admin.ModelAdmin):
    list_display = ('description', 'rate', 'quantity', 'tax', 'subtotal')
    actions = (actions.undo_billing, actions.move_lines, actions.copy_lines,)
    
    def get_queryset(self, request):
        qset = super(BillLineManagerAdmin, self).get_queryset(request)
        return qset.filter(bill_id__in=self.bill_ids)
    
    def changelist_view(self, request, extra_context=None):
        GET = request.GET.copy()
        bill_ids = GET.pop('bill_ids', ['0'])[0]
        request.GET = GET
        bill_ids = [int(id) for id in bill_ids.split(',')]
        self.bill_ids = bill_ids
        if not bill_ids:
            return
        elif len(bill_ids) > 1:
            title = _("Manage bill lines of multiple bills.")
        else:
            bill_url = reverse('admin:bills_bill_change', args=(bill_ids[0],))
            bill = Bill.objects.get(pk=bill_ids[0])
            bill_link = '<a href="%s">%s</a>' % (bill_url, bill.ident)
            title = mark_safe(_("Manage %s bill lines.") % bill_link)
        context = {
            'title': title,
        }
        context.update(extra_context or {})
        return super(BillLineManagerAdmin, self).changelist_view(request, context)


class BillAdmin(AccountAdminMixin, ExtendedModelAdmin):
    list_display = (
        'number', 'type_link', 'account_link', 'created_on_display',
        'num_lines', 'display_total', 'display_payment_state', 'is_open', 'is_sent'
    )
    list_filter = (BillTypeListFilter, 'is_open', 'is_sent')
    add_fields = ('account', 'type', 'is_open', 'due_on', 'comments')
    fieldsets = (
        (None, {
            'fields': ('number', 'type', 'account_link', 'display_total',
                       'display_payment_state', 'is_sent', 'due_on', 'comments'),
        }),
        (_("Raw"), {
            'classes': ('collapse',),
            'fields': ('html',),
        }),
    )
    change_view_actions = [
        actions.view_bill, actions.download_bills, actions.send_bills, actions.close_bills
    ]
    search_fields = ('number', 'account__username', 'comments')
    actions = [actions.download_bills, actions.close_bills, actions.send_bills]
    change_readonly_fields = ('account_link', 'type', 'is_open')
    readonly_fields = ('number', 'display_total', 'is_sent', 'display_payment_state')
    inlines = [BillLineInline, ClosedBillLineInline]
    
    created_on_display = admin_date('created_on')
    
    def num_lines(self, bill):
        return bill.lines__count
    num_lines.admin_order_field = 'lines__count'
    num_lines.short_description = _("lines")
    
    def display_total(self, bill):
        return "%s &%s;" % (round(bill.computed_total or 0, 2), settings.BILLS_CURRENCY.lower())
    display_total.allow_tags = True
    display_total.short_description = _("total")
    display_total.admin_order_field = 'computed_total'
    
    def type_link(self, bill):
        bill_type = bill.type.lower()
        url = reverse('admin:bills_%s_changelist' % bill_type)
        return '<a href="%s">%s</a>' % (url, bill.get_type_display())
    type_link.allow_tags = True
    type_link.short_description = _("type")
    type_link.admin_order_field = 'type'
    
    def display_payment_state(self, bill):
        t_opts = bill.transactions.model._meta
        transactions = bill.transactions.all()
        if len(transactions) == 1:
            args = (transactions[0].pk,)
            url = reverse('admin:%s_%s_change' % (t_opts.app_label, t_opts.model_name), args=args)
        else:
            url = reverse('admin:%s_%s_changelist' % (t_opts.app_label, t_opts.model_name))
            url += '?bill=%i' % bill.pk
        state = bill.get_payment_state_display().upper()
        color = PAYMENT_STATE_COLORS.get(bill.payment_state, 'grey')
        return '<a href="{url}" style="color:{color}">{name}</a>'.format(
                url=url, color=color, name=state)
    display_payment_state.allow_tags = True
    display_payment_state.short_description = _("Payment")
    
    def get_urls(self):
        """ Hook bill lines management URLs on bill admin """
        urls = super(BillAdmin, self).get_urls()
        admin_site = self.admin_site
        extra_urls = patterns("",
            url("^manage-lines/$",
                admin_site.admin_view(BillLineManagerAdmin(BillLine, admin_site).changelist_view),
                name='bills_bill_manage_lines'),
        )
        return extra_urls + urls
    
    def get_readonly_fields(self, request, obj=None):
        fields = super(BillAdmin, self).get_readonly_fields(request, obj)
        if obj and not obj.is_open:
            fields += self.add_fields
        return fields
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super(BillAdmin, self).get_fieldsets(request, obj)
        if obj and obj.is_open:
            fieldsets = (fieldsets[0],)
        return fieldsets
    
    def get_change_view_actions(self, obj=None):
        actions = super(BillAdmin, self).get_change_view_actions(obj)
        exclude = []
        if obj:
            if not obj.is_open:
                exclude.append('close_bills')
        return [action for action in actions if action.__name__ not in exclude]
    
    def get_inline_instances(self, request, obj=None):
        inlines = super(BillAdmin, self).get_inline_instances(request, obj)
        if obj and not obj.is_open:
            return [inline for inline in inlines if type(inline) is not BillLineInline]
        return [inline for inline in inlines if type(inline) is not ClosedBillLineInline]
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'comments':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 4})
        if db_field.name == 'html':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 150, 'rows': 20})
        return super(BillAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        
    def get_queryset(self, request):
        qs = super(BillAdmin, self).get_queryset(request)
        qs = qs.annotate(
            models.Count('lines'),
            computed_total=Sum(
                (F('lines__subtotal') + Coalesce(F('lines__sublines__total'), 0)) * (1+F('lines__tax')/100)
            ),
        )
        qs = qs.prefetch_related('transactions')
        return qs
    
    def change_view(self, request, object_id, **kwargs):
        # TODO raise404, here and everywhere
        bill = self.get_object(request, unquote(object_id))
        actions.validate_contact(request, bill, error=False)
        return super(BillAdmin, self).change_view(request, object_id, **kwargs)


admin.site.register(Bill, BillAdmin)
admin.site.register(Invoice, BillAdmin)
admin.site.register(AmendmentInvoice, BillAdmin)
admin.site.register(Fee, BillAdmin)
admin.site.register(AmendmentFee, BillAdmin)
admin.site.register(ProForma, BillAdmin)


class BillContactInline(admin.StackedInline):
    model = BillContact
    fields = ('name', 'address', ('city', 'zipcode'), 'country', 'vat')
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'name':
            kwargs['widget'] = forms.TextInput(attrs={'size':'70'})
        if db_field.name == 'address':
            kwargs['widget'] = forms.Textarea(attrs={'cols': 70, 'rows': 2})
        if db_field.name == 'email_usage':
            kwargs['widget'] = paddingCheckboxSelectMultiple(45)
        return super(BillContactInline, self).formfield_for_dbfield(db_field, **kwargs)


def has_bill_contact(account):
    return hasattr(account, 'billcontact')
has_bill_contact.boolean = True
has_bill_contact.admin_order_field = 'billcontact'


insertattr(AccountAdmin, 'inlines', BillContactInline)
insertattr(AccountAdmin, 'list_display', has_bill_contact)
insertattr(AccountAdmin, 'list_filter', HasBillContactListFilter)
