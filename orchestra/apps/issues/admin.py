from __future__ import absolute_import

from django import forms
from django.conf.urls import patterns
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from markdown import markdown

from orchestra.admin import ChangeListDefaultFilter, ExtendedModelAdmin#, ChangeViewActions
from orchestra.admin.utils import (link, colored, wrap_admin_view, display_timesince)

from .actions import (reject_tickets, resolve_tickets, take_tickets, close_tickets,
    mark_as_unread, mark_as_read, set_default_queue)
from .filters import MyTicketsListFilter, TicketStateListFilter
from .forms import MessageInlineForm, TicketForm
from .helpers import get_ticket_changes, markdown_formated_changes, filter_actions
from .models import Ticket, Queue, Message


PRIORITY_COLORS = { 
    Ticket.HIGH: 'red',
    Ticket.MEDIUM: 'darkorange',
    Ticket.LOW: 'green',
}


STATE_COLORS = { 
    Ticket.NEW: 'grey',
    Ticket.IN_PROGRESS: 'darkorange',
    Ticket.FEEDBACK: 'purple',
    Ticket.RESOLVED: 'green',
    Ticket.REJECTED: 'firebrick',
    Ticket.CLOSED: 'grey',
}


class MessageReadOnlyInline(admin.TabularInline):
    model = Message
    extra = 0
    can_delete = False
    fields = ['content_html']
    readonly_fields = ['content_html']
    
    class Media:
        css = {
            'all': ('orchestra/css/hide-inline-id.css',)
        }
    
    def content_html(self, obj):
        context = {
            'number': obj.number,
            'time': display_timesince(obj.created_on),
            'author': link('author')(self, obj),
        }
        summary = _("#%(number)i Updated by %(author)s about %(time)s") % context
        header = '<strong style="color:#666;">%s</strong><hr />' % summary
        content = markdown(obj.content)
        content = content.replace('>\n', '>')
        content = '<div style="padding-left:20px;">%s</div>' % content
        return header + content
    content_html.short_description = _("Content")
    content_html.allow_tags = True

    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    max_num = 1
    form = MessageInlineForm
    can_delete = False
    fields = ['content']
    
    def get_formset(self, request, obj=None, **kwargs):
        """ hook request.user on the inline form """
        self.form.user = request.user
        return super(MessageInline, self).get_formset(request, obj, **kwargs)
    
    def queryset(self, request):
        """ Don't show any message """
        qs = super(MessageInline, self).queryset(request)
        return qs.none()


class TicketInline(admin.TabularInline):
    fields = [
        'ticket_id', 'subject', 'creator_link', 'owner_link', 'colored_state',
        'colored_priority', 'created', 'last_modified'
    ]
    readonly_fields =  [
        'ticket_id', 'subject', 'creator_link', 'owner_link', 'colored_state',
        'colored_priority', 'created', 'last_modified'
    ]
    model = Ticket
    extra = 0
    max_num = 0
    
    creator_link = link('creator')
    owner_link = link('owner')
    
    def ticket_id(self, instance):
        return mark_safe('<b>%s</b>' % link()(self, instance))
    ticket_id.short_description = '#'
    
    def colored_state(self, instance):
        return colored('state', STATE_COLORS, bold=False)(instance)
    colored_state.short_description = _("State")
    
    def colored_priority(self, instance):
        return colored('priority', PRIORITY_COLORS, bold=False)(instance)
    colored_priority.short_description = _("Priority")
    
    def created(self, instance):
        return display_timesince(instance.created_on)
    
    def last_modified(self, instance):
        return display_timesince(instance.last_modified_on)


class TicketAdmin(ChangeListDefaultFilter, ExtendedModelAdmin): #TODO ChangeViewActions, 
    list_display = [
        'unbold_id', 'bold_subject', 'display_creator', 'display_owner',
        'display_queue', 'display_priority', 'display_state', 'last_modified'
    ]
    list_display_links = ('unbold_id', 'bold_subject')
    list_filter = [
        MyTicketsListFilter, 'queue__name', 'priority', TicketStateListFilter,
    ]
    default_changelist_filters = (
        ('my_tickets', lambda r: 'True' if not r.user.is_superuser else 'False'),
        ('state', 'OPEN')
    )
    date_hierarchy = 'created_on'
    search_fields = [
        'id', 'subject', 'creator__username', 'creator__email', 'queue__name',
        'owner__username'
    ]
    actions = [
        mark_as_unread, mark_as_read, 'delete_selected', reject_tickets,
        resolve_tickets, close_tickets, take_tickets
    ]
    sudo_actions = ['delete_selected']
    change_view_actions = [
        resolve_tickets, close_tickets, reject_tickets, take_tickets
    ]
#    change_form_template = "admin/orchestra/change_form.html"
    form = TicketForm
    add_inlines = []
    inlines = [ MessageReadOnlyInline, MessageInline ]
    readonly_fields = (
        'display_summary', 'display_queue', 'display_owner', 'display_state',
        'display_priority'
    )
    readonly_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('display_summary',
                       ('display_queue', 'display_owner'),
                       ('display_state', 'display_priority'),
                       'display_description')
        }),
    )
    fieldsets = readonly_fieldsets + (
        ('Update', {
            'classes': ('collapse', 'wide'),
            'fields': ('subject',
                      ('queue', 'owner',),
                      ('state', 'priority'),
                       'description')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('subject',
                      ('queue', 'owner',),
                      ('state', 'priority'),
                      'description')
        }),
    )
    
    class Media:
        css = {
            'all': ('issues/css/ticket-admin.css',)
        }
        js = (
            'issues/js/ticket-admin.js',
        )
    
    display_creator = link('creator')
    display_queue = link('queue')
    display_owner = link('owner')
    
    def display_summary(self, ticket):
        author_url = link('creator')(self, ticket)
        created = display_timesince(ticket.created_on)
        messages = ticket.messages.order_by('-created_on')
        updated = ''
        if messages:
            updated_on = display_timesince(messages[0].created_on)
            updated_by = link('author')(self, messages[0])
            updated = '. Updated by %s about %s' % (updated_by, updated_on)
        msg = '<h4>Added by %s about %s%s</h4>' % (author_url, created, updated)
        return mark_safe(msg)
    display_summary.short_description = 'Summary'
    
    def display_priority(self, ticket):
        """ State colored for change_form """
        return colored('priority', PRIORITY_COLORS, bold=False, verbose=True)(ticket)
    display_priority.short_description = _("Priority")
    display_priority.admin_order_field = 'priority'
    
    def display_state(self, ticket):
        """ State colored for change_form """
        return colored('state', STATE_COLORS, bold=False, verbose=True)(ticket)
    display_state.short_description = _("State")
    display_state.admin_order_field = 'state'
    
    def unbold_id(self, ticket):
        """ Unbold id if ticket is read """
        if ticket.is_read_by(self.user):
            return '<span style="font-weight:normal;font-size:11px;">%s</span>' % ticket.pk
        return ticket.pk
    unbold_id.allow_tags = True
    unbold_id.short_description = "#"
    unbold_id.admin_order_field = 'id'
    
    def bold_subject(self, ticket):
        """ Bold subject when tickets are unread for request.user """
        if ticket.is_read_by(self.user):
            return ticket.subject
        return "<strong class='unread'>%s</strong>" % ticket.subject
    bold_subject.allow_tags = True
    bold_subject.short_description = _("Subject")
    bold_subject.admin_order_field = 'subject'
    
    def last_modified(self, instance):
        return display_timesince(instance.last_modified_on)
    last_modified.admin_order_field = 'last_modified_on'
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Make value input widget bigger """
        if db_field.name == 'subject':
            kwargs['widget'] = forms.TextInput(attrs={'size':'120'})
        return super(TicketAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def save_model(self, request, obj, *args, **kwargs):
        """ Define creator for new tickets """
        if not obj.pk:
            obj.creator = request.user
        super(TicketAdmin, self).save_model(request, obj, *args, **kwargs)
        obj.mark_as_read_by(request.user)
    
    def get_urls(self):
        """ add markdown preview url """
        urls = super(TicketAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^preview/$', wrap_admin_view(self, self.message_preview_view))
        )
        return my_urls + urls
    
    def add_view(self, request, form_url='', extra_context=None):
        """ Do not sow message inlines """
        return super(TicketAdmin, self).add_view(request, form_url, extra_context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """ Change view actions based on ticket state """
        ticket = get_object_or_404(Ticket, pk=object_id)
        # Change view actions based on ticket state
        self.change_view_actions = filter_actions(self, ticket, request)
        if request.method == 'POST':
            # Hack: Include the ticket changes on the request.POST
            #       other approaches get really messy
            changes = get_ticket_changes(self, request, ticket)
            if changes:
                content = markdown_formated_changes(changes)
                content += request.POST[u'messages-2-0-content']
                request.POST[u'messages-2-0-content'] = content
        ticket.mark_as_read_by(request.user)
        context = {'title': "Issue #%i - %s" % (ticket.id, ticket.subject)}
        context.update(extra_context or {})
        return super(TicketAdmin, self).change_view(
            request, object_id, form_url, extra_context=context)
    
    def changelist_view(self, request, extra_context=None):
        # Hook user for bold_subject
        self.user = request.user
        return super(TicketAdmin,self).changelist_view(request, extra_context=extra_context)
    
    def message_preview_view(self, request):
        """ markdown preview render via ajax """
        data = request.POST.get("data")
        data_formated = markdown(strip_tags(data))
        return HttpResponse(data_formated)


class QueueAdmin(admin.ModelAdmin):
    # TODO notify
    list_display = [
        'name', 'default', 'num_tickets'
    ]
    actions = [set_default_queue]
    inlines = [TicketInline]
    ordering = ['name']
    
    class Media:
        css = {
            'all': ('orchestra/css/hide-inline-id.css',)
        }
    
    def num_tickets(self, queue):
        num = queue.tickets.count()
        url = reverse('admin:issues_ticket_changelist')
        url += '?my_tickets=False&queue=%i' % queue.pk
        return mark_safe('<a href="%s">%d</a>' % (url, num))
    num_tickets.short_description = _("Tickets")
    num_tickets.admin_order_field = 'tickets__count'
    
    def queryset(self, request):
        qs = super(QueueAdmin, self).queryset(request)
        qs = qs.annotate(models.Count('tickets'))
        return qs


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Queue, QueueAdmin)
