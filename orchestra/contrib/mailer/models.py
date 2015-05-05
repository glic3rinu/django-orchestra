from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import settings


class Message(models.Model):
    QUEUED = 'QUEUED'
    SENT = 'SENT'
    DEFERRED = 'DEFERRED'
    FAILED = 'FAILED'
    STATES = (
        (QUEUED, _("Queued")),
        (SENT, _("Sent")),
        (DEFERRED, _("Deferred")),
        (FAILED, _("Failes")),
    )
    
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    PRIORITIES = (
        (CRITICAL, _("Critical (not queued)")),
        (HIGH, _("High")),
        (NORMAL, _("Normal")),
        (LOW, _("Low")),
    )
    
    state = models.CharField(_("State"), max_length=16, choices=STATES, default=QUEUED)
    priority = models.PositiveIntegerField(_("Priority"), choices=PRIORITIES, default=NORMAL)
    to_address = models.CharField(max_length=256)
    from_address = models.CharField(max_length=256)
    subject = models.CharField(_("subject"), max_length=256)
    content = models.TextField(_("content"))
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    retries = models.PositiveIntegerField(_("retries"), default=0)
    # TODO rename to last_try
    last_retry = models.DateTimeField(_("last try"), auto_now=True)
    
    def defer(self):
        self.state = self.DEFERRED
        # Max tries
        if self.retries >= len(settings.MAILER_DEFERE_SECONDS):
            self.state = self.FAILED
        self.save(update_fields=('state', 'retries'))
    
    def sent(self):
        self.state = self.SENT
        self.save(update_fields=('state',))
    
    def log(self, error):
        result = SMTPLog.SUCCESS
        if error:
            result= SMTPLog.FAILURE
        self.logs.create(log_message=str(error), result=result)


class SMTPLog(models.Model):
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    RESULTS = (
        (SUCCESS, _("Success")),
        (FAILURE, _("Failure")),
    )
    message = models.ForeignKey(Message, editable=False, related_name='logs')
    result = models.CharField(max_length=16, choices=RESULTS, default=SUCCESS)
    date = models.DateTimeField(auto_now_add=True)
    log_message = models.TextField()
