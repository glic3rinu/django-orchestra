from django.apps import AppConfig

from orchestra.core import administration


class MailerConfig(AppConfig):
    name = 'orchestra.contrib.mailer'
    verbose_name = "Mailer"
    
    def ready(self):
        from .models import Message
        administration.register(Message, icon='Mail-send.png')
