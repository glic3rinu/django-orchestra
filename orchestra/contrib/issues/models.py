from django.conf import settings as djsettings
from django.db import models
from django.db.models import query, Q
from django.utils.translation import ugettext_lazy as _

from orchestra.contrib.contacts import settings as contacts_settings
from orchestra.contrib.contacts.models import Contact
from orchestra.models.fields import MultiSelectField
from orchestra.utils.mail import send_email_template

from . import settings


class Queue(models.Model):
    name = models.CharField(_("name"), max_length=128, unique=True)
    verbose_name = models.CharField(_("verbose_name"), max_length=128, blank=True)
    default = models.BooleanField(_("default"), default=False)
    notify = MultiSelectField(_("notify"), max_length=256, blank=True,
        choices=Contact.EMAIL_USAGES,
        default=contacts_settings.CONTACTS_DEFAULT_EMAIL_USAGES,
        help_text=_("Contacts to notify by email"))
    
    def __str__(self):
        return self.verbose_name or self.name
    
    def save(self, *args, **kwargs):
        """ mark as default queue if needed """
        existing_default = Queue.objects.filter(default=True)
        if self.default:
            existing_default.update(default=False)
        elif not existing_default:
            self.default = True
        super(Queue, self).save(*args, **kwargs)


class TicketQuerySet(query.QuerySet):
    def involved_by(self, user, *args, **kwargs):
        qset = Q(creator=user) | Q(owner=user) | Q(messages__author=user)
        return self.filter(qset, *args, **kwargs).distinct()


class Ticket(models.Model):
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'
    PRIORITIES = (
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    )
    
    NEW = 'NEW'
    IN_PROGRESS = 'IN_PROGRESS'
    RESOLVED = 'RESOLVED'
    FEEDBACK = 'FEEDBACK'
    REJECTED = 'REJECTED'
    CLOSED = 'CLOSED'
    STATES = (
        (NEW, 'New'),
        (IN_PROGRESS, 'In Progress'),
        (RESOLVED, 'Resolved'),
        (FEEDBACK, 'Feedback'),
        (REJECTED, 'Rejected'),
        (CLOSED, 'Closed'),
    )
    
    creator = models.ForeignKey(djsettings.AUTH_USER_MODEL, verbose_name=_("created by"),
        related_name='tickets_created', null=True, on_delete=models.SET_NULL)
    creator_name = models.CharField(_("creator name"), max_length=256, blank=True)
    owner = models.ForeignKey(djsettings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='tickets_owned', verbose_name=_("assigned to"))
    queue = models.ForeignKey(Queue, related_name='tickets', null=True, blank=True,
        on_delete=models.SET_NULL)
    subject = models.CharField(_("subject"), max_length=256)
    description = models.TextField(_("description"))
    priority = models.CharField(_("priority"), max_length=32, choices=PRIORITIES, default=MEDIUM)
    state = models.CharField(_("state"), max_length=32, choices=STATES, default=NEW)
    created_at = models.DateTimeField(_("created"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("modified"), auto_now=True)
    cc = models.TextField("CC", help_text=_("emails to send a carbon copy to"), blank=True)
    
    objects = TicketQuerySet.as_manager()
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return str(self.pk)
    
    def get_notification_emails(self):
        """ Get emails of the users related to the ticket """
        emails = list(settings.ISSUES_SUPPORT_EMAILS)
        emails.append(self.creator.email)
        if self.owner:
            emails.append(self.owner.email)
        for contact in self.creator.contacts.all():
            if self.queue and set(contact.email_usage).union(set(self.queue.notify)):
                emails.append(contact.email)
        for message in self.messages.distinct('author'):
            emails.append(message.author.email)
        return set(emails + self.get_cc_emails())
        
    def notify(self, message=None, content=None):
        """ Send an email to ticket stakeholders notifying an state update """
        emails = self.get_notification_emails()
        template = 'issues/ticket_notification.mail'
        html_template = 'issues/ticket_notification_html.mail'
        context = {
            'ticket': self,
            'ticket_message': message
        }
        send_email_template(template, context, emails, html=html_template)
    
    def save(self, *args, **kwargs):
        """ notify stakeholders of new ticket """
        new_issue = not self.pk
        if not self.creator_name and self.creator:
            self.creator_name = self.creator.get_full_name()
        super(Ticket, self).save(*args, **kwargs)
        if new_issue:
            # PK should be available for rendering the template
            self.notify()
    
    def is_involved_by(self, user):
        """ returns whether user has participated or is referenced on the ticket
            as owner or member of the group
        """
        return Ticket.objects.filter(pk=self.pk).involved_by(user).exists()
    
    def get_cc_emails(self):
        return self.cc.split(',') if self.cc else []
    
    def mark_as_read_by(self, user):
        self.trackers.get_or_create(user=user)
    
    def mark_as_unread_by(self, user):
        self.trackers.filter(user=user).delete()
    
    def mark_as_unread(self):
        self.trackers.all().delete()
    
    def is_read_by(self, user):
        return self.trackers.filter(user=user).exists()
    
    def reject(self):
        self.state = Ticket.REJECTED
        self.save(update_fields=('state', 'updated_at'))
    
    def resolve(self):
        self.state = Ticket.RESOLVED
        self.save(update_fields=('state', 'updated_at'))
    
    def close(self):
        self.state = Ticket.CLOSED
        self.save(update_fields=('state', 'updated_at'))
    
    def take(self, user):
        self.owner = user
        self.save(update_fields=('state', 'updated_at'))


class Message(models.Model):
    ticket = models.ForeignKey('issues.Ticket', verbose_name=_("ticket"),
        related_name='messages')
    author = models.ForeignKey(djsettings.AUTH_USER_MODEL, verbose_name=_("author"),
        related_name='ticket_messages')
    author_name = models.CharField(_("author name"), max_length=256, blank=True)
    content = models.TextField(_("content"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    
    class Meta:
        get_latest_by = 'id'
    
    def __str__(self):
        return "#%i" % self.id
    
    def save(self, *args, **kwargs):
        """ notify stakeholders of ticket update """
        if not self.pk:
            self.ticket.mark_as_unread()
            self.ticket.mark_as_read_by(self.author)
            self.ticket.notify(message=self)
            self.author_name = self.author.get_full_name()
        super(Message, self).save(*args, **kwargs)
    
    @property
    def number(self):
        return self.ticket.messages.filter(id__lte=self.id).count()


class TicketTracker(models.Model):
    """ Keeps track of user read tickets """
    ticket = models.ForeignKey(Ticket, verbose_name=_("ticket"), related_name='trackers')
    user = models.ForeignKey(djsettings.AUTH_USER_MODEL, verbose_name=_("user"),
        related_name='ticket_trackers')
    
    class Meta:
        unique_together = (
            ('ticket', 'user'),
        )
