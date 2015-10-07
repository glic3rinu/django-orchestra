from django.apps import AppConfig

from orchestra.core import services


class MailboxesConfig(AppConfig):
    name = 'orchestra.contrib.mailboxes'
    verbose_name = 'Mailboxes'
    
    def ready(self):
        from .models import Mailbox, Address
        services.register(Mailbox, icon='email.png')
        services.register(Address, icon='X-office-address-book.png')
        from . import signals
