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
        for message in email_messages:
            priority = message.extra_headers.get('X-Mail-Priority', Message.NORMAL)
            content = message.message().as_string()
            for to_email in message.recipients():
                message = Message.objects.create(
                    priority=priority,
                    to_address=to_email,
                    from_address=message.from_email,
                    subject=message.subject,
                    content=content,
                )
                if not is_bulk or priority == Message.CRITICAL:
                    # send immidiately
                    send_message.apply_async(message)
            num_sent += 1
        return num_sent
