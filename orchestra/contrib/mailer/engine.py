import smtplib
from datetime import timedelta
from socket import error as SocketError

from django.core.mail import get_connection
from django.db.models import Q
from django.utils import timezone
from django.utils.encoding import smart_str

from orchestra.utils.sys import LockFile, OperationLocked

from . import settings
from .models import Message


def send_message(message, connection=None, bulk=settings.MAILER_BULK_MESSAGES):
    message.last_try = timezone.now()
    update_fields = ['last_try']
    if message.state != message.QUEUED:
        message.retries += 1
        update_fields.append('retries')
    message.save(update_fields=update_fields)
    if connection is None:
        connection = get_connection(backend='django.core.mail.backends.smtp.EmailBackend')
    if connection.connection is None:
        try:
            connection.open()
        except Exception as err:
            message.defer()
            message.log(err)
            return
    error = None
    try:
        connection.connection.sendmail(message.from_address, [message.to_address], smart_str(message.content))
    except (SocketError,
            smtplib.SMTPSenderRefused,
            smtplib.SMTPRecipientsRefused,
            smtplib.SMTPAuthenticationError) as err:
        message.defer()
        error = err
    else:
        message.sent()
    message.log(error)
    return connection


def send_pending(bulk=settings.MAILER_BULK_MESSAGES):
    try:
        with LockFile('/dev/shm/mailer.send_pending.lock'):
            connection = get_connection(backend='django.core.mail.backends.smtp.EmailBackend')
            cur, total = 0, 0
            for message in Message.objects.filter(state=Message.QUEUED).order_by('priority', 'last_try', 'created_at'):
                if cur >= bulk:
                    connection.close()
                    cur = 0
                send_message(message, connection, bulk)
                cur += 1
                total += 1
            now = timezone.now()
            qs = Q()
            for retries, seconds in enumerate(settings.MAILER_DEFERE_SECONDS):
                delta = timedelta(seconds=seconds)
                qs = qs | Q(retries=retries, last_try__lte=now-delta)
            for message in Message.objects.filter(state=Message.DEFERRED).filter(qs).order_by('priority', 'last_try'):
                if cur >= bulk:
                    connection.close()
                    cur = 0
                send_message(message, connection, bulk)
                cur += 1
                total += 1
        return total
    except OperationLocked:
        pass
    finally:
        if 'connection' in vars() and connection.connection is not None:
            connection.close()
