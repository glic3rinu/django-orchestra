from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from .models import Ticket


class MyTicketsListFilter(SimpleListFilter):
    """ Filter tickets by created_by according to request.user """
    title = 'Tickets'
    parameter_name = 'my_tickets'
    
    def lookups(self, request, model_admin):
        return (
            ('True', _("My Tickets")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.involved_by(request.user)


class TicketStateListFilter(SimpleListFilter):
    title = 'State'
    parameter_name = 'state'
    
    def lookups(self, request, model_admin):
        return (
            ('OPEN', _("Open")),
            (Ticket.NEW, _("New")),
            (Ticket.IN_PROGRESS, _("In Progress")),
            (Ticket.RESOLVED, _("Resolved")),
            (Ticket.FEEDBACK, _("Feedback")),
            (Ticket.REJECTED, _("Rejected")),
            (Ticket.CLOSED, _("Closed")),
            ('False', _("All")),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'OPEN':
            return queryset.exclude(state__in=[Ticket.CLOSED, Ticket.REJECTED])
        elif self.value() == 'False':
            return queryset
        return queryset.filter(state=self.value())
    
    def choices(self, cl):
        """ Remove default All """
        choices = iter(super(TicketStateListFilter, self).choices(cl))
        next(choices)
        return choices
