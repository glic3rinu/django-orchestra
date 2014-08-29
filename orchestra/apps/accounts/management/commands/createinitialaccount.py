from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from orchestra.apps.accounts.models import Account
from orchestra.apps.users.models import User


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--noinput', action='store_false', dest='interactive',
                        default=True),
            make_option('--username', action='store', dest='username'),
            make_option('--password', action='store', dest='password'),
            make_option('--email', action='store', dest='email'),
        )
    
    option_list = BaseCommand.option_list
    help = 'Used to create an initial account and its user.'
    
    @transaction.atomic
    def handle(self, *args, **options):
        interactive = options.get('interactive')
        if not interactive:
            email = options.get('email')
            username = options.get('username')
            password = options.get('password')
            account = Account.objects.create()
            user = User.objects.create_superuser(username, email, password,
                    account=account, is_main=True)
