import sys

from django.contrib import messages
from django.db import transaction

from orchestra.admin.decorators import action_with_confirmation

from .forms import ChangeReasonForm
from .helpers import markdown_formated_changes
from .models import Queue, Ticket


def change_ticket_state_factory(action, final_state):
    context = {
        'action': action,
        'form': ChangeReasonForm()
    }
    @transaction.atomic
    @action_with_confirmation(action, extra_context=context)
    def change_ticket_state(modeladmin, request, queryset, action=action, final_state=final_state):
        form = ChangeReasonForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            for ticket in queryset:
                if ticket.state != final_state:
                    changes = {'state': (ticket.state, final_state)}
                    is_read = ticket.is_read_by(request.user)
                    getattr(ticket, action)()
                    modeladmin.log_change(request, ticket, "Marked as %s" % final_state.lower())
                    content = markdown_formated_changes(changes)
                    content += reason
                    ticket.messages.create(content=content, author=request.user)
                    if is_read and not ticket.is_read_by(request.user):
                        ticket.mark_as_read_by(request.user)
            msg = "%s selected tickets are now %s." % (queryset.count(), final_state.lower())
            modeladmin.message_user(request, msg)
        else:
            context['form'] = form
            # action_with_confirmation must display form validation errors
            return True
    change_ticket_state.url_name = action
    change_ticket_state.verbose_name = u'%s\u2026' % action
    change_ticket_state.short_description = '%s selected tickets' % action.capitalize()
    change_ticket_state.description = 'Mark ticket as %s.' % final_state.lower()
    change_ticket_state.__name__ = action
    return change_ticket_state


action_map = {
    Ticket.RESOLVED: 'resolve',
    Ticket.REJECTED: 'reject',
    Ticket.CLOSED: 'close' }


thismodule = sys.modules[__name__]
for state, name in action_map.items():
    action = change_ticket_state_factory(name, state)
    setattr(thismodule, '%s_tickets' % name, action)


@transaction.atomic
def take_tickets(modeladmin, request, queryset):
    for ticket in queryset:
        if ticket.owner != request.user:
            changes = {'owner': (ticket.owner, request.user)}
            is_read = ticket.is_read_by(request.user)
            ticket.take(request.user)
            modeladmin.log_change(request, ticket, "Taken")
            content = markdown_formated_changes(changes)
            ticket.messages.create(content=content, author=request.user)
            if is_read and not ticket.is_read_by(request.user):
                ticket.mark_as_read_by(request.user)
    msg = "%s selected tickets are now owned by %s." % (queryset.count(), request.user)
    modeladmin.message_user(request, msg)
take_tickets.url_name = 'take'
take_tickets.short_description = 'Take selected tickets'
take_tickets.description = 'Make yourself owner of the ticket.'


@transaction.atomic
def mark_as_unread(modeladmin, request, queryset):
    """ Mark a tickets as unread """
    for ticket in queryset:
        ticket.mark_as_unread_by(request.user)
    msg = "%s selected tickets have been marked as unread." % queryset.count()
    modeladmin.message_user(request, msg)


@transaction.atomic
def mark_as_read(modeladmin, request, queryset):
    """ Mark a tickets as unread """
    for ticket in queryset:
        ticket.mark_as_read_by(request.user)
    msg = "%s selected tickets have been marked as read." % queryset.count()
    modeladmin.message_user(request, msg)


@transaction.atomic
def set_default_queue(modeladmin, request, queryset):
    """ Set a queue as default issues queue """
    if queryset.count() != 1:
        messages.warning(request, "Please, select only one queue.")
        return
    Queue.objects.filter(default=True).update(default=False)
    queue = queryset.get()
    queue.default = True
    queue.save()
    modeladmin.log_change(request, queue, "Chosen as default.")
    messages.info(request, "Chosen '%s' as default queue." % queue)
