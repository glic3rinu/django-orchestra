from django.conf import settings as djsettings
from django.core.mail.backends.base import BaseEmailBackend

from .models import Message
from .tasks import send_message


class EmailBackend(BaseEmailBackend):
    """
    A wrapper that manages a queued SMTP system.
    """
    def send_messages(self, email_messages):
        if not email_messages:
            return
        num_sent = 0
        is_bulk = len(email_messages) > 1
        default_priority = Message.NORMAL if is_bulk else Message.CRITICAL
        for message in email_messages:
            priority = message.extra_headers.get('X-Mail-Priority', default_priority)
            content = message.message().as_string()
            for to_email in message.recipients():
                message = Message.objects.create(
                    priority=priority,
                    to_address=to_email,
                    from_address=getattr(message, 'from_email', djsettings.DEFAULT_FROM_EMAIL),
                    subject=message.subject,
                    content=content,
                )
                if priority == Message.CRITICAL:
                    # send immidiately
                    send_message.apply_async(message)
            num_sent += 1
        return num_sent
