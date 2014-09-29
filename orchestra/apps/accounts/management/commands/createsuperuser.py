from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands import createsuperuser

from orchestra.apps.accounts.models import Account


class Command(createsuperuser.Command):
    def handle(self, *args, **options):
        super(Command, self).handle(*args, **options)
        raise NotImplementedError
        users = get_user_model().objects.filter()
        if len(users) == 1 and not Account.objects.all().exists():
            user = users[0]
            user.account = Account.objects.create(user=user)
            user.save()
