"""
Chpasswd command for existing mail users to change their password.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

from django.db.models.loading import get_model

from orchestra.apps.mails.settings import MAILS_VIRTUAL_MAILBOX, MAILS_VIRTUAL_MAILDOMAIN

class Command(BaseCommand):
    args = 'email password new_password'
    help = ('Reset a mail users password, given their email address\n'
            'and current password. By default the passwords must be\n'
            'supplied in clear-text, and are cryptographically hashed\n'
            'by chpasswd.')

    def handle(self, *args, **options):
        usage = 'Required arguments: email password new_password'
        if len(args) != 3:
            raise CommandError(usage)

        email, curr, new = args
        Mailbox = get_model(MAILS_VIRTUAL_MAILBOX.split(".")[0],
                            MAILS_VIRTUAL_MAILBOX.split(".")[1])
        MailDomain = get_model(MAILS_VIRTUAL_MAILDOMAIN.split(".")[0],
                            MAILS_VIRTUAL_MAILDOMAIN.split(".")[1])
        try:
            user = Mailbox.get_from_email(email)
        except ValidationError:
            raise CommandError('Improperly formatted email address.')
        except MailDomain.DoesNotExist:
            raise CommandError('Domain does not exist.')
        except Mailbox.DoesNotExist:
            raise CommandError('Username does not exist.')

        authorized = user.check_password(curr)
        if not authorized:
            raise CommandError('Incorrect password.')

        user.set_password(new)
        user.save()
        self.stdout.write('Success.\n')
