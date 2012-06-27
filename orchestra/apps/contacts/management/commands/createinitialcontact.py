from contacts.models import Contact, Contract
from django.contrib.auth.models import User
from django.core import exceptions
from django.core.management.base import BaseCommand, CommandError
from django.db import models
from django.utils.translation import ugettext as _
import sys


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            # Get a username
            while 1:
                input_msg = 'Name'
                name = raw_input(input_msg + ': ')
                try:
                    Contact.objects.get(name=name)
                except Contact.DoesNotExist:
                    break
                else:
                    sys.stderr.write("Error: That contact name is already taken.\n")
                    username = None
        except KeyboardInterrupt:
            sys.stderr.write("\nOperation cancelled.\n")
            sys.exit(1)

        contact = Contact(name=name)
        contact.save()
        Contract.create(contact=contact, obj=contact).save()
        user = User.objects.get(pk=1)
        Contract.create(contact=contact, obj=user).save()
