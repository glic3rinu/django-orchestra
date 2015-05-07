from django.apps import AppConfig

from orchestra.core import accounts


class ContactsConfig(AppConfig):
    name = 'orchestra.contrib.contacts'
    verbose_name = 'Contacts'
    
    def ready(self):
        from .models import Contact
        accounts.register(Contact, icon='contact_book.png')
