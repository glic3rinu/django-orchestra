from functools import partial

from django.contrib import messages
from django.db import transaction
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ungettext, ugettext_lazy as _

from orchestra.admin.decorators import action_with_confirmation
from orchestra.admin.utils import change_url

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
            method = PaymentMethod.get(method)
            procs = method.process(transactions)
            processes += procs
            for trans in transactions:
                modeladmin.log_change(request, trans, _("Processed"))
    if not processes:
        return
    opts = modeladmin.model._meta
    num = len(queryset)
    context = {
        'title': ungettext(
            _("Selected transaction has been processed."),
            _("%s Selected transactions have been processed.") % num,
            num),
        'content_message': ungettext(
            _("The following transaction process has been generated, "
              "you may want to save it on your computer now."),
            _("The following %s transaction processes have been generated, "
              "you may want to save it on your computer now.") % len(processes),
            len(processes)),
        'action_name': _("Process"),
        'processes': processes,
        'opts': opts,
        'app_label': opts.app_label,
    }
    return render(request, 'admin/payments/transaction/get_processes.html', context)


@transaction.atomic
@action_with_confirmation()
def mark_as_executed(modeladmin, request, queryset):
    for trans in queryset:
        trans.mark_as_executed()
        modeladmin.log_change(request, trans, _("Executed"))
    num = len(queryset)
    msg = ungettext(
        _("One selected transaction has been marked as executed."),
        _("%s selected transactions have been marked as executed.") % num,
        num)
    modeladmin.message_user(request, msg)
mark_as_executed.url_name = 'execute'
mark_as_executed.verbose_name = _("Mark as executed")


@transaction.atomic
@action_with_confirmation()
def mark_as_secured(modeladmin, request, queryset):
    for trans in queryset:
        trans.mark_as_secured()
        modeladmin.log_change(request, trans, _("Secured"))
    num = len(queryset)
    msg = ungettext(
        _("One selected transaction has been marked as secured."),
        _("%s selected transactions have been marked as secured.") % num,
        num)
    modeladmin.message_user(request, msg)
mark_as_secured.url_name = 'secure'
mark_as_secured.verbose_name = _("Mark as secured")


@transaction.atomic
@action_with_confirmation()
def mark_as_rejected(modeladmin, request, queryset):
    for trans in queryset:
        trans.mark_as_rejected()
        modeladmin.log_change(request, trans, _("Rejected"))
    num = len(queryset)
    msg = ungettext(
        _("One selected transaction has been marked as rejected."),
        _("%s selected transactions have been marked as rejected.") % num,
        num)
    modeladmin.message_user(request, msg)
mark_as_rejected.url_name = 'reject'
mark_as_rejected.verbose_name = _("Mark as rejected")


def _format_display_objects(modeladmin, request, queryset, related):
    objects = []
    opts = modeladmin.model._meta
    for obj in queryset:
        objects.append(
            mark_safe('{0}: <a href="{1}">{2}</a>'.format(
                capfirst(opts.verbose_name), change_url(obj), obj))
        )
        subobjects = []
        attr, verb = related
        for related in getattr(obj.transactions, attr)():
            subobjects.append(
                mark_safe('Transaction: <a href="{}">{}</a> will be marked as {}'.format(
                    change_url(related), related, verb))
            )
        objects.append(subobjects)
    return {'display_objects': objects}

_format_executed = partial(_format_display_objects, related=('all', 'executed'))
_format_abort = partial(_format_display_objects, related=('processing', 'aborted'))
_format_commit = partial(_format_display_objects, related=('all', 'secured'))


@transaction.atomic
@action_with_confirmation(extra_context=_format_executed)
def mark_process_as_executed(modeladmin, request, queryset):
    for process in queryset:
        process.mark_as_executed()
        modeladmin.log_change(request, process, _("Executed"))
    num = len(queryset)
    msg = ungettext(
        _("One selected process has been marked as executed."),
        _("%s selected processes have been marked as executed.") % num,
        num)
    modeladmin.message_user(request, msg)
mark_process_as_executed.url_name = 'executed'
mark_process_as_executed.verbose_name = _("Mark as executed")


@transaction.atomic
@action_with_confirmation(extra_context=_format_abort)
def abort(modeladmin, request, queryset):
    for process in queryset:
        process.abort()
        modeladmin.log_change(request, process, _("Aborted"))
    num = len(queryset)
    msg = ungettext(
        _("One selected process has been aborted."),
        _("%s selected processes have been aborted.") % num,
        num)
    modeladmin.message_user(request, msg)
abort.url_name = 'abort'
abort.verbose_name = _("Abort")


@transaction.atomic
@action_with_confirmation(extra_context=_format_commit)
def commit(modeladmin, request, queryset):
    for trans in queryset:
        trans.mark_as_rejected()
        modeladmin.log_change(request, trans, _("Rejected"))
    num = len(queryset)
    msg = ungettext(
        _("One selected transaction has been marked as rejected."),
        _("%s selected transactions have been marked as rejected.") % num,
        num)
    modeladmin.message_user(request, msg)
commit.url_name = 'commit'
commit.verbose_name = _("Commit")
