from common.utils.file import download_files
from datetime import datetime
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, QueryDict
from django.utils.translation import ugettext as _
from models import Bill, BudgetLine, Budget
from payment.plugins import PaymentMethod
from views import delete_lines_view
import settings


def get_bill_class(bill_line_cls):
    if bill_line_cls is BudgetLine: return Budget
    else: return Bill


@transaction.commit_on_success                       
def manual_amend_line(modeladmin, request, queryset):
    if len(queryset) != 1:
        messages.add_message(request, messages.ERROR, _("Bills must be selected on at a time" ))
    else: 
        return HttpResponseRedirect("./add_amended/%s/" % queryset[0].pk)


@transaction.commit_on_success                       
def auto_amend_total_value(modeladmin, request, queryset):
    bill_lines = []
    for line in queryset:
        bill_lines.append(line.auto_create_amend())
    print modeladmin.model
    bills = Bill.create(line.bill.contact, bill_lines)
    modeladmin.message_user(request, _("All lines are amended" ))


@transaction.commit_on_success 
def delete_lines(modeladmin, request, queryset):
    return delete_lines_view(modeladmin, request, queryset)


@transaction.commit_on_success
def move_lines(modeladmin, request, queryset, extra_context=None):
    """ Show contact list with links to add view + contact_id=x """ 
    bill_cls = get_bill_class(modeladmin.model)
    # Reset querydict to avoid ?e=1    
    request.GET=QueryDict('')
    bill_id = request.META['PATH_INFO'].split('/manage_lines')[0].split('/')[-1]
    bill = bill_cls.objects.get(pk=bill_id)
    if bill.__class__ is Budget:
        bill_cls_lower = 'budget'
    else:
        bill_cls_lower = bill.subclass_instance.__class__.__name__.lower()
    
    _queryset = ""
    for obj in queryset:    
        _queryset += "%s," % (obj.pk)
    
    url = "/admin/billing/%s/%s/select_to_move/?q=%s&queryset=%s" % (bill_cls_lower, bill_id, bill.contact.name, _queryset[:-1])
    return HttpResponseRedirect(url)    


@transaction.commit_on_success                 
def amend_selected(modeladmin, request, queryset): pass


@transaction.commit_on_success                 
def merge_selected(modeladmin, request, queryset):
    if len(queryset) < 2: 
        messages.add_message(request, messages.ERROR, _("Select at least 2 bills" ))
        return
    merged = queryset[0]
    for bill in queryset[1:]:
        for line in bill.lines.all():
            line.bill = merged
            line.save()
        bill.delete()
    modeladmin.message_user(request, _("Selected bills are successfully merged" ))


@transaction.commit_manually
def mark_as_returned(modeladmin, request, queryset): 
    for bill in queryset:
        if bill.status != settings.SEND:
            messages.add_message(request, messages.ERROR, _("The bill must be sent" ))
            transaction.rollback()
            return
        bill.mark_as_returned()
    transaction.commit()
    modeladmin.message_user(request, _("Selected bills marked as returned" ))


@transaction.commit_on_success             
def mark_as_payd(modeladmin, request, queryset): 
    for bill in queryset:
        bill.mark_as_payd()
    modeladmin.message_user(request, _("Selected bills marked as payd" ))


@transaction.commit_on_success         
def mark_as_irrecovrable(modeladmin, request, queryset):
    for bill in queryset:
        bill.mark_as_irrecovrable()
    modeladmin.message_user(request, _("Selected bills marked as Irrecovrable" ))


@transaction.commit_on_success                 
def close_selected(modeladmin, request, queryset):
    for bill in queryset:
        if modeladmin.model is Bill:
            bill = bill.subclass_instance
        bill.close()
    modeladmin.message_user(request, _("Selected Bills Succesfully closed" ))


@transaction.commit_on_success             
def send_selected(modeladmin, request, queryset):
    for bill in queryset:
        bill.send()
    modeladmin.message_user(request, _("Selected Bills Succesfully Send" ))


@transaction.commit_on_success
def bulk_download(modeladmin, request, queryset):
    files = []
    for bill in queryset:
        files.append({'filename': "%s.pdf" % bill.ident,
                      'file': bill.get_pdf()})
    
    return download_files(files, mimetype='application/pdf')
bulk_download.short_description = _('Download')
