import StringIO
import zipfile

from django.contrib import messages
from django.contrib.admin import helpers
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.forms import adminmodelformset_factory
from orchestra.utils.html import html_to_pdf

from .forms import SelectSourceForm


def download_bills(modeladmin, request, queryset):
    if queryset.count() > 1:
        stringio = StringIO.StringIO()
        archive = zipfile.ZipFile(stringio, 'w')
        for bill in queryset:
            html = bill.html or bill.render()
            pdf = html_to_pdf(html)
            archive.writestr('%s.pdf' % bill.number, pdf)
        archive.close()
        response = HttpResponse(stringio.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="orchestra-bills.zip"'
        return response
    bill = queryset.get()
    pdf = html_to_pdf(bill.html)
    return HttpResponse(pdf, content_type='application/pdf')
download_bills.verbose_name = _("Download")
download_bills.url_name = 'download'


def view_bill(modeladmin, request, queryset):
    bill = queryset.get()
    html = bill.html or bill.render()
    return HttpResponse(html)
view_bill.verbose_name = _("View")
view_bill.url_name = 'view'


def close_bills(modeladmin, request, queryset):
    queryset = queryset.filter(status=queryset.model.OPEN)
    if not queryset:
        messages.warning(request, _("Selected bills should be in open state"))
        return
    SelectSourceFormSet = adminmodelformset_factory(modeladmin, SelectSourceForm,
            extra=0)
    formset = SelectSourceFormSet(queryset=queryset)
    if request.POST.get('post') == 'yes':
        formset = SelectSourceFormSet(request.POST, request.FILES, queryset=queryset)
        if formset.is_valid():
            for form in formset.forms:
                source = form.cleaned_data['source']
                form.instance.close(payment=source)
            messages.success(request, _("Selected bills have been closed"))
            return
    opts = modeladmin.model._meta
    context = {
        'title': "Are you sure?",
        'action_value': 'close_bills',
        'deletable_objects': queryset,
        'queryset': queryset,
        'opts': opts,
        'app_label': opts.app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        'formset': formset,
    }
    # TODO use generic confirmation template
    return render(request, 'admin/bills/close_confirmation.html', context)
close_bills.verbose_name = _("Close")
close_bills.url_name = 'close'


def send_bills(modeladmin, request, queryset):
    for bill in queryset:
        bill.send()
send_bills.verbose_name = _("Send")
send_bills.url_name = 'send'
