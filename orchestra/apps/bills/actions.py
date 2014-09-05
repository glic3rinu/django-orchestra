import StringIO
import zipfile

from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from orchestra.utils.html import html_to_pdf


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


from django import forms
from django.forms.models import BaseModelFormSet
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.shortcuts import render

from .forms import SelectPaymentSourceForm

def close_bills(modeladmin, request, queryset):
    queryset = queryset.filter(status=queryset.model.OPEN)
    if not queryset:
        messages.warning(request, _("Selected bills should be in open state"))
        return
    SelectPaymentSourceFormSet = modelformset_factory(queryset.model, form=SelectPaymentSourceForm, extra=0)
    if request.POST.get('action') == 'close_selected_bills':
        formset = SelectPaymentSourceFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            for form in formset.forms:
                form.save()
            messages.success(request, _("Selected bills have been closed"))
            return
    formset = SelectPaymentSourceFormSet(queryset=queryset)
    return render(request, 'admin/bills/close_confirmation.html', {'formset': formset})
close_bills.verbose_name = _("Close")
close_bills.url_name = 'close'


def send_bills(modeladmin, request, queryset):
    for bill in queryset:
        bill.send()
send_bills.verbose_name = _("Send")
send_bills.url_name = 'send'
