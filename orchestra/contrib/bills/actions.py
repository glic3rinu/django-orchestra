import io
import zipfile
from datetime import date

from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms.models import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import translation, timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.admin.decorators import action_with_confirmation
from orchestra.admin.forms import AdminFormSet
from orchestra.admin.utils import get_object_from_url, change_url

from . import settings
from .forms import SelectSourceForm
from .helpers import validate_contact, set_context_emails
from .models import Bill, BillLine


def view_bill(modeladmin, request, queryset):
    bill = queryset.get()
    if not validate_contact(request, bill):
        return
    html = bill.html or bill.render()
    return HttpResponse(html)
view_bill.tool_description = _("View")
view_bill.url_name = 'view'
view_bill.hidden = True


@transaction.atomic
def close_bills(modeladmin, request, queryset, action='close_bills'):
    # Validate bills
    for bill in queryset:
        if not validate_contact(request, bill):
            return False
        if not bill.is_open:
            messages.warning(request, _("Selected bills should be in open state"))
            return False
    SelectSourceFormSet = modelformset_factory(modeladmin.model, form=SelectSourceForm, formset=AdminFormSet, extra=0)
    formset = SelectSourceFormSet(queryset=queryset)
    if request.POST.get('post') == 'generic_confirmation':
        formset = SelectSourceFormSet(request.POST, request.FILES, queryset=queryset)
        if formset.is_valid():
            transactions = []
            for form in formset.forms:
                source = form.cleaned_data['source']
                transaction = form.instance.close(payment=source)
                if transaction:
                    transactions.append(transaction)
            for bill in queryset:
                modeladmin.log_change(request, bill, 'Closed')
            messages.success(request, _("Selected bills have been closed"))
            if transactions:
                num = len(transactions)
                if num == 1:
                    url = change_url(transactions[0])
                else:
                    url = reverse('admin:payments_transaction_changelist')
                    url += 'id__in=%s' % ','.join([str(t.id) for t in transactions])
                context = {
                    'url': url,
                    'num': num,
                }
                message = ungettext(
                    _('<a href="%(url)s">One related transaction</a> has been created') % context,
                    _('<a href="%(url)s">%(num)i related transactions</a> have been created') % context,
                    num)
                messages.success(request, mark_safe(message))
            return
    opts = modeladmin.model._meta
    context = {
        'title': _("Are you sure about closing the following bills?"),
        'content_message': _("Once a bill is closed it can not be further modified.</p>"
                             "<p>Please select a payment source for the selected bills"),
        'action_name': 'Close bills',
        'action_value': action,
        'display_objects': [],
        'queryset': queryset,
        'opts': opts,
        'app_label': opts.app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'formset': formset,
        'obj': get_object_from_url(modeladmin, request),
    }
    template = 'admin/orchestra/generic_confirmation.html'
    if action == 'close_send_download_bills':
        template = 'admin/bills/bill/close_send_download_bills.html'
    return render(request, template, context)
close_bills.tool_description = _("Close")
close_bills.url_name = 'close'


def send_bills_action(modeladmin, request, queryset):
    """
    raw function without confirmation
    enables reuse on close_send_download_bills because of generic_confirmation.action_view
    """
    for bill in queryset:
        if not validate_contact(request, bill):
            return False
    num = 0
    for bill in queryset:
        bill.send()
        modeladmin.log_change(request, bill, 'Sent')
        num += 1
    messages.success(request, ungettext(
        _("One bill has been sent."),
        _("%i bills have been sent.") % num,
        num))


@action_with_confirmation(extra_context=set_context_emails)
def send_bills(modeladmin, request, queryset):
    return send_bills_action(modeladmin, request, queryset)
send_bills.verbose_name = lambda bill: _("Resend" if getattr(bill, 'is_sent', False) else "Send")
send_bills.url_name = 'send'


def download_bills(modeladmin, request, queryset):
    for bill in queryset:
        if not validate_contact(request, bill):
            return False
    if len(queryset) > 1:
        bytesio = io.BytesIO()
        archive = zipfile.ZipFile(bytesio, 'w')
        for bill in queryset:
            pdf = bill.as_pdf()
            archive.writestr('%s.pdf' % bill.number, pdf)
        archive.close()
        response = HttpResponse(bytesio.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="orchestra-bills.zip"'
        return response
    bill = queryset[0]
    pdf = bill.as_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % bill.number
    return response
download_bills.tool_description = _("Download")
download_bills.url_name = 'download'


def close_send_download_bills(modeladmin, request, queryset):
    response = close_bills(modeladmin, request, queryset, action='close_send_download_bills')
    if response is False:
        # Not a valid contact or closed bill
        return
    if request.POST.get('post') == 'generic_confirmation':
        response = send_bills_action(modeladmin, request, queryset)
        if response is False:
            # Not a valid contact
            return
        return download_bills(modeladmin, request, queryset)
    return response
close_send_download_bills.tool_description = _("C.S.D.")
close_send_download_bills.url_name = 'close-send-download'
close_send_download_bills.help_text = _("Close, send and download bills in one shot.")


def manage_lines(modeladmin, request, queryset):
    url = reverse('admin:bills_bill_manage_lines')
    url += '?ids=%s' % ','.join(map(str, queryset.values_list('id', flat=True)))
    return redirect(url)


@action_with_confirmation()
def undo_billing(modeladmin, request, queryset):
    group = {}
    for line in queryset.select_related('order'):
        if line.order_id:
            try:
                group[line.order].append(line)
            except KeyError:
                group[line.order] = [line]
    
    # Validate
    for order, lines in group.items():
        prev = None
        billed_on = date.max
        billed_until = date.max
        for line in sorted(lines, key=lambda l: l.start_on):
            if billed_on is not None:
                if line.order_billed_on is None:
                    billed_on = line.order_billed_on
                else:
                    billed_on = min(billed_on, line.order_billed_on)
            if billed_until is not None:
                if line.order_billed_until is None:
                    billed_until = line.order_billed_until
                else:
                    billed_until = min(billed_until, line.order_billed_until)
            if prev:
                if line.start_on != prev:
                    messages.error(request, "Line dates doesn't match.")
                    return
            else:
                # First iteration
                if order.billed_on < line.start_on:
                    messages.error(request, "Billed on is smaller than first line start_on.")
                    return
            prev = line.end_on
            nlines += 1
        if not prev:
            messages.error(request, "Order does not have lines!.")
        order.billed_until = billed_until
        order.billed_on = billed_on
    
    # Commit changes
    norders, nlines = 0, 0
    for order, lines in group.items():
        for line in lines:
            nlines += 1
            line.delete()
        # TODO update order history undo billing
        order.save(update_fields=('billed_until', 'billed_on'))
        norders += 1
    
    messages.success(request, _("%(norders)s orders and %(nlines)s lines undoed.") % {
        'nlines': nlines,
        'norders': norders
    })


def move_lines(modeladmin, request, queryset, action=None):
    # Validate
    target = request.GET.get('target')
    if not target:
        # select target
        context = {}
        return render(request, 'admin/orchestra/generic_confirmation.html', context)
    target = Bill.objects.get(pk=int(pk))
    if request.POST.get('post') == 'generic_confirmation':
        for line in queryset:
            line.bill = target
            line.save(update_fields=['bill'])
        # TODO bill history update
        messages.success(request, _("Lines moved"))
    # Final confirmation
    return render(request, 'admin/orchestra/generic_confirmation.html', context)


def copy_lines(modeladmin, request, queryset):
    # same as move, but changing action behaviour
    return move_lines(modeladmin, request, queryset)


def validate_amend_bills(bills):
    for bill in bills:
        if bill.is_open:
            raise ValidationError(_("Selected bills should be in closed state"))
        if bill.type not in bill.AMEND_MAP:
            raise ValidationError(_("%s can not be amended.") % bill.get_type_display())


@action_with_confirmation(validator=validate_amend_bills)
def amend_bills(modeladmin, request, queryset):
    amend_ids = []
    for bill in queryset:
        with translation.override(bill.account.language):
            amend_type = bill.get_amend_type()
            context = {
                'related_type': _(bill.get_type_display()),
                'number': bill.number,
                'date': bill.created_on,
            }
            amend = Bill.objects.create(
                account=bill.account,
                type=amend_type,
                amend_of=bill,
            )
            context['type'] = _(amend.get_type_display())
            amend.comments = _("%(type)s of %(related_type)s %(number)s and creation date %(date)s") % context
            amend.save(update_fields=('comments',))
            for tax, subtotals in bill.compute_subtotals().items():
                context['tax'] = tax
                line = BillLine.objects.create(
                    bill=amend,
                    start_on=bill.created_on,
                    description=_("%(related_type)s %(number)s subtotal for tax %(tax)s%%") % context,
                    subtotal=subtotals[0],
                    tax=tax
                )
            amend_ids.append(amend.pk)
        modeladmin.log_change(request, bill, 'Amended, amend id is %i' % amend.id)
    num = len(amend_ids)
    if num == 1:
        amend_url = reverse('admin:bills_bill_change', args=amend_ids)
    else:
        amend_url = reverse('admin:bills_bill_changelist')
        amend_url += '?id=%s' % ','.join(map(str, amend_ids))
    context = {
        'url': amend_url,
        'num': num,
    }
    messages.success(request, mark_safe(ungettext(
        _('<a href="%(url)s">One amendment bill</a> have been generated.') % context,
        _('<a href="%(url)s">%(num)i amendment bills</a> have been generated.') % context,
        num
    )))
amend_bills.tool_description = _("Amend")
amend_bills.url_name = 'amend'


def bill_report(modeladmin, request, queryset):
    subtotals = {}
    total = 0
    for bill in queryset:
        for tax, subtotal in bill.compute_subtotals().items():
            try:
                subtotals[tax][0] += subtotal[0]
            except KeyError:
                subtotals[tax] = subtotal
            else:
                subtotals[tax][1] += subtotal[1]
        total += bill.compute_total()
    context = {
        'subtotals': subtotals,
        'total': total,
        'bills': queryset,
        'currency': settings.BILLS_CURRENCY,
    }
    return render(request, 'admin/bills/bill/report.html', context)


def service_report(modeladmin, request, queryset):
    services = {}
    totals = [0, 0, 0, 0, 0]
    now = timezone.now().date()
    if queryset.model == Bill:
        queryset = BillLine.objects.filter(bill_id__in=queryset.values_list('id', flat=True))
    # Filter amends
    queryset = queryset.filter(bill__amend_of__isnull=True)
    for line in queryset.select_related('order__service').prefetch_related('sublines'):
        order, service = None, None
        if line.order_id:
            order = line.order
            service = order.service
            name = service.description
            active, cancelled = (1, 0) if not order.cancelled_on or order.cancelled_on > now else (0, 1)
            nominal_price = order.service.nominal_price
        else:
            name = '*%s' % line.description
            active = 1
            cancelled = 0
            nominal_price = 0
        try:
            info = services[name]
        except KeyError:
            info = [active, cancelled, nominal_price, line.quantity or 1, line.compute_total()]
            services[name] = info
        else:
            info[0] += active
            info[1] += cancelled
            info[3] += line.quantity or 1
            info[4] += line.compute_total()
        totals[0] += active
        totals[1] += cancelled
        totals[2] += nominal_price
        totals[3] += line.quantity or 1
        totals[4] += line.compute_total()
    context = {
        'services': sorted(services.items(), key=lambda n: -n[1][4]),
        'totals': totals,
    }
    return render(request, 'admin/bills/billline/report.html', context)


def list_bills(modeladmin, request, queryset):
    ids = ','.join(map(str, queryset.values_list('bill_id', flat=True).distinct()))
    return HttpResponseRedirect('../bill/?id__in=%s' % ids)
