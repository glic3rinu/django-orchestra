from django.contrib.auth import models as auth_app
from contacts import models as contacts_app
from django.db.models import get_models, signals

def create_contact(app, created_models, verbosity, **kwargs):
    from django.core.management import call_command

    if contacts_app.Contact and contacts_app.Contract and auth_app.User in created_models and kwargs.get('interactive', True):
        msg = ("\nYou just installed Django ISP Tools Contacts system, which means you "
            "don't have any Contact defined.\nWould you like to create one now? (yes/no): ")
        confirm = raw_input(msg)
        while 1:
            if confirm not in ('yes', 'no'):
                confirm = raw_input('Please enter either "yes" or "no": ')
                continue
            if confirm == 'yes':
                call_command("createinitialcontact", interactive=True)
            break


signals.post_syncdb.connect(create_contact,
    sender=contacts_app, dispatch_uid = "contacts.management.createinitialcontact")

