from orchestra.apps.accounts.models import Account
from orchestra.apps.users.models import User
from orchestra.utils.tests import BaseTestCase, random_ascii


class BaseBillingTest(BaseTestCase):
    def create_account(self):
        account = Account.objects.create()
        username = 'account_%s' % random_ascii(5)
        user = User.objects.create_user(username=username, account=account)
        account.user = user
        account.save()
        return account


# TODO web disk
