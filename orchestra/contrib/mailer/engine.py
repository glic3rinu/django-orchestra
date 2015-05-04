import smtplib
from socket import error as SocketError

from django.core.mail import get_connection
from django.utils.encoding import smart_str

from .models import Message


def send_message(message, num, connection, bulk):
    if num >= bulk:
        connection.close()
        connection = None
    if connection is None:
        # Reset connection with django 
        connection = get_connection(backend='django.core.mail.backends.smtp.EmailBackend')
        connection.open()
    error = None
    try:
        connection.connection.sendmail(message.from_address, [message.to_address], smart_str(message.content))
    except (SocketError, smtplib.SMTPSenderRefused,
            smtplib.SMTPRecipientsRefused,
            smtplib.SMTPAuthenticationError) as err:
        message.defer()
        error = err
    else:
        message.sent()
    message.log(error)


def send_pending(bulk=100):
    # TODO aquire lock
    connection = None
    num = 0
    for message in Message.objects.filter(state=Message.QUEUED).order_by('priority'):
        send_message(message, num, connection, bulk)
    from django.utils import timezone
    from . import settings
    from datetime import timedelta
    from django.db.models import Q
    
    now = timezone.now()
    qs = Q()
    for retries, seconds in enumerate(settings.MAILER_DEFERE_SECONDS):
        delta = timedelta(seconds=seconds)
        qs = qs | Q(retries=retries, last_retry__lte=now-delta)
    for message in Message.objects.filter(state=Message.DEFERRED).filter(qs).order_by('priority'):
        send_message(message, num, connection, bulk)
    if connection is not None:
        connection.close()

