from django.contrib import messages
from django.db import transaction
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from orchestra.admin.decorators import action_with_confirmation

from .methods import PaymentMethod
from .models import Transaction


@transaction.atomic
def process_transactions(modeladmin, request, queryset):
    processes = []
    if queryset.exclude(state=Transaction.WAITTING_PROCESSING).exists():
        msg = _("Selected transactions must be on '{state}' state")
        messages.error(request, msg.format(state=Transaction.WAITTING_PROCESSING))
        return
    for method, transactions in queryset.group_by('source__method').iteritems():
        if method is not None:
            method = PaymentMethod.get_plugin(method)
            procs = method.process(transactions)
            processes += procs
            for transaction in transactions:
                modeladmin.log_change(request, transaction, 'Processed')
    if not processes:
        return
    opts = modeladmin.model._meta
    context = {
        'title': _("Huston, be advised"),
        'action_name': _("Process"),
        'processes': processes,
        'opts': opts,
        'app_label': opts.app_label,
    }
    return render(request, 'admin/payments/transaction/get_processes.html', context)


@transaction.atomic
@action_with_confirmation()
def mark_as_executed(modeladmin, request, queryset):
    """ Mark a tickets as unread """
    for transaction in queryset:
        transaction.mark_as_executed()
        modeladmin.log_change(request, transaction, 'Executed')
    msg = _("%s selected transactions have been marked as executed.") % queryset.count()
    modeladmin.message_user(request, msg)
mark_as_executed.url_name = 'execute'
mark_as_executed.verbose_name = _("Mark as executed")


@transaction.atomic
@action_with_confirmation()
def mark_as_secured(modeladmin, request, queryset):
    """ Mark a tickets as unread """
    for transaction in queryset:
        transaction.mark_as_secured()
        modeladmin.log_change(request, transaction, 'Secured')
    msg = _("%s selected transactions have been marked as secured.") % queryset.count()
    modeladmin.message_user(request, msg)
mark_as_secured.url_name = 'secure'
mark_as_secured.verbose_name = _("Mark as secured")


@transaction.atomic
@action_with_confirmation()
def mark_as_rejected(modeladmin, request, queryset):
    """ Mark a tickets as unread """
    for transaction in queryset:
        transaction.mark_as_rejected()
        modeladmin.log_change(request, transaction, 'Rejected')
    msg = _("%s selected transactions have been marked as rejected.") % queryset.count()
    modeladmin.message_user(request, msg)
mark_as_rejected.url_name = 'reject'
mark_as_rejected.verbose_name = _("Mark as rejected")
