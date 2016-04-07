from django.contrib import messages
from django.utils.translation import ungettext, ugettext_lazy as _

from .models import Transaction


def pre_delete_processes(modeladmin, request, queryset):
    """ Has to have same name as admin.actions.delete_selected """
    if not queryset:
        messages.warning(request,
            _("No transaction process selected."))
        return
    if queryset.exclude(transactions__state=Transaction.WAITTING_EXECUTION).exists():
        messages.error(request,
            _("Done nothing. Not all related transactions in waitting execution."))
        return
    # Store before deleting
    related_transactions = []
    for process in queryset:
        waitting_execution = process.transactions.filter(state=Transaction.WAITTING_EXECUTION)
        related_transactions.extend(waitting_execution)
    return related_transactions


def post_delete_processes(modeladmin, request, related_transactions):
    # Confirmation
    num = 0
    for transaction in related_transactions:
        transaction.state = Transaction.WAITTING_PROCESSING
        transaction.save(update_fields=('state', 'modified_at'))
        num += 1
        modeladmin.log_change(request, transaction, _("Unprocessed"))
    messages.success(request, ungettext(
        "One related transaction has been marked as <i>waitting for processing</i>",
        "%i related transactions have been marked as <i>waitting for processing</i>." % num,
        num
    ))
