import StringIO
import zipfile

from django.contrib import messages
from django.contrib.admin import helpers
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.admin.forms import adminmodelformset_factory
from orchestra.admin.utils import get_object_from_url, change_url
from orchestra.utils.html import html_to_pdf

from .forms import SelectSourceForm
from .helpers import validate_contact


def download_bills(modeladmin, request, queryset):
    if queryset.count() > 1:
        stringio = StringIO.StringIO()
        archive = zipfile.ZipFile(stringio, 'w')
        for bill in queryset:
            pdf = html_to_pdf(bill.html or bill.render())
            archive.writestr('%s.pdf' % bill.number, pdf)
        archive.close()
        response = HttpResponse(stringio.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="orchestra-bills.zip"'
        return response
    bill = queryset.get()
    pdf = html_to_pdf(bill.html or bill.render())
    return HttpResponse(pdf, content_type='application/pdf')
download_bills.verbose_name = _("Download")
download_bills.url_name = 'download'


def view_bill(modeladmin, request, queryset):
    bill = queryset.get()
    if not validate_contact(request, bill):
        return
    html = bill.html or bill.render()
    return HttpResponse(html)
view_bill.verbose_name = _("View")
view_bill.url_name = 'view'


@transaction.atomic
def close_bills(modeladmin, request, queryset):
    queryset = queryset.filter(is_open=True)
    if not queryset:
        messages.warning(request, _("Selected bills should be in open state"))
        return
    for bill in queryset:
        if not validate_contact(request, bill):
            return
    SelectSourceFormSet = adminmodelformset_factory(modeladmin, SelectSourceForm, extra=0)
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
                    url = reverse('admin:transactions_transaction_changelist')
                    url += 'id__in=%s' % ','.join([str(t.id) for t in transactions])
                message = ungettext(
                    _('<a href="%s">One related transaction</a> has been created') % url,
                    _('<a href="%s">%i related transactions</a> have been created') % (url, num),
                    num)
                messages.success(request, mark_safe(message))
            return
    opts = modeladmin.model._meta
    context = {
        'title': _("Are you sure about closing the following bills?"),
        'content_message': _("Once a bill is closed it can not be further modified.</p>"
                             "<p>Please select a payment source for the selected bills"),
        'action_name': 'Close bills',
        'action_value': 'close_bills',
        'display_objects': [],
        'queryset': queryset,
        'opts': opts,
        'app_label': opts.app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'formset': formset,
        'obj': get_object_from_url(modeladmin, request),
    }
    return render(request, 'admin/orchestra/generic_confirmation.html', context)
close_bills.verbose_name = _("Close")
close_bills.url_name = 'close'


def send_bills(modeladmin, request, queryset):
    for bill in queryset:
        if not validate_contact(request, bill):
            return
    for bill in queryset:
        bill.send()
        modeladmin.log_change(request, bill, 'Sent')
send_bills.verbose_name = lambda bill: _("Resend" if getattr(bill, 'is_sent', False) else "Send")
send_bills.url_name = 'send'


def undo_billing(modeladmin, request, queryset):
    group = {}
    for line in queryset.select_related('order'):
        if line.order_id:
            try:
                group[line.order].append(line)
            except KeyError:
                group[line.order] = [line]
    # TODO force incomplete info
    for order, lines in group.iteritems():
        # Find path from ini to end
        for attr in ['order_id', 'order_billed_on', 'order_billed_until']:
            if not getattr(self, attr):
                raise ValidationError(_("Not enough information stored for undoing"))
        sorted(lines, key=lambda l: l.created_on)
        if 'a' != order.billed_on:
            raise ValidationError(_("Dates don't match"))
        prev = order.billed_on
        for ix in xrange(0, len(lines)):
            if lines[ix].order_b: # TODO we need to look at the periods here
                pass
        order.billed_until = self.order_billed_until
        order.billed_on = self.order_billed_on

# TODO son't check for account equality
def move_lines(modeladmin, request, queryset):
    # Validate
    account = None
    for line in queryset.select_related('bill'):
        bill = line.bill
        if bill.state != bill.OPEN:
            messages.error(request, _("Can not move lines which are not in open state."))
            return 
        elif not account:
            account = bill.account
        elif bill.account != account:
            messages.error(request, _("Can not move lines from different accounts"))
            return
    target = request.GET.get('target')
    if not target:
        # select target
        return render(request, 'admin/orchestra/generic_confirmation.html', context)
    target = Bill.objects.get(pk=int(pk))
    if target.account != account:
        messages.error(request, _("Target account different than lines account."))
        return
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
    pass


def delete_lines(modeladmin, request, queryset):
    pass
