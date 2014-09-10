from django.contrib import messages
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from .methods import PaymentMethod
from .models import Transaction

def process_transactions(modeladmin, request, queryset):
    processes = []
    if queryset.exclude(state=Transaction.WAITTING_PROCESSING).exists():
        msg = _("Selected transactions must be on '{state}' state")
        messages.error(request, msg.format(state=Transaction.WAITTING_PROCESSING))
        return
    for method, transactions in queryset.group_by('source__method'):
        if method is not None:
            method = PaymentMethod.get_plugin(method)
            procs = method.process(transactions)
            processes += procs
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
