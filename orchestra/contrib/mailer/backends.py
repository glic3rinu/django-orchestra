from django.conf import settings as djsettings
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend

from orchestra.core.caches import get_request_cache

from . import settings
from .models import Message
from .tasks import send_message


class EmailBackend(BaseEmailBackend):
    """
    A wrapper that manages a queued SMTP system.
    """
    def send_messages(self, email_messages):
        if not email_messages:
            return
        # Count messages per request
        cache = get_request_cache()
        key = 'mailer.sent_messages'
        sent_messages = cache.get(key) or 0
        sent_messages += 1
        cache.set(key, sent_messages)
        
        is_bulk = len(email_messages) > 1
        if sent_messages > settings.MAILER_NON_QUEUED_PER_REQUEST_THRESHOLD:
            is_bulk = True
        default_priority = Message.NORMAL if is_bulk else Message.CRITICAL
        num_sent = 0
        connection = None
        for message in email_messages:
            priority = message.extra_headers.get('X-Mail-Priority', default_priority)
            content = message.message().as_string()
            for to_email in message.recipients():
                message = Message(
                    priority=priority,
                    to_address=to_email,
                    from_address=getattr(message, 'from_email', djsettings.DEFAULT_FROM_EMAIL),
                    subject=message.subject,
                    content=content,
                )
                if priority == Message.CRITICAL:
                    # send immidiately
                    if connection is None:
                        connection = get_connection(backend='django.core.mail.backends.smtp.EmailBackend')
                    send_message.apply_async(message, connection=connection)
                else:
                    message.save()
            num_sent += 1
        if connection is not None:
            connection.close()
        return num_sent
