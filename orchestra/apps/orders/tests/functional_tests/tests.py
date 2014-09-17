import datetime
import decimal
import sys

from dateutil import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from orchestra.apps.accounts.models import Account
from orchestra.apps.services.models import Service
from orchestra.apps.services import settings as services_settings
from orchestra.apps.users.models import User
from orchestra.utils.tests import BaseTestCase, random_ascii


class ServiceTests(BaseTestCase):
    DEPENDENCIES = (
        'orchestra.apps.services',
        'orchestra.apps.users',
        'orchestra.apps.users.roles.posix',
    )
    
    def create_account(self):
        account = Account.objects.create()
        user = User.objects.create_user(username='rata_palida', account=account)
        account.user = user
        account.save()
        return account
    
    def create_ftp_service(self):
        service = Service.objects.create(
            description="FTP Account",
            content_type=ContentType.objects.get_for_model(User),
            match='not user.is_main and user.has_posix()',
            billing_period=Service.ANUAL,
            billing_point=Service.FIXED_DATE,
            is_fee=False,
            metric='',
            pricing_period=Service.BILLING_PERIOD,
            rate_algorithm=Service.STEP_PRICE,
            on_cancel=Service.DISCOUNT,
            payment_style=Service.PREPAY,
            tax=0,
            nominal_price=10,
        )
        return service
    
    def create_ftp(self, account=None):
        username = '%s_ftp' % random_ascii(10)
        if not account:
            account = self.create_account()
        user = User.objects.create_user(username=username, account=account)
        POSIX = user._meta.get_field_by_name('posix')[0].model
        POSIX.objects.create(user=user)
        return user
    
    def test_ftp_account_1_year_fiexed(self):
        service = self.create_ftp_service()
        user = self.create_ftp()
        bp = timezone.now().date() + relativedelta.relativedelta(years=1)
        bills = service.orders.bill(billing_point=bp, fixed_point=True)
        self.assertEqual(10, bills[0].get_total())
    
    def test_ftp_account_2_year_fiexed(self):
        service = self.create_ftp_service()
        user = self.create_ftp()
        bp = timezone.now().date() + relativedelta.relativedelta(years=2)
        bills = service.orders.bill(billing_point=bp, fixed_point=True)
        self.assertEqual(20, bills[0].get_total())
    
    def test_ftp_account_6_month_fixed(self):
        service = self.create_ftp_service()
        self.create_ftp()
        bp = timezone.now().date() + relativedelta.relativedelta(months=6)
        bills = service.orders.bill(billing_point=bp, fixed_point=True)
        self.assertEqual(5, bills[0].get_total())
    
    def test_ftp_account_next_billing_point(self):
        service = self.create_ftp_service()
        self.create_ftp()
        now = timezone.now()
        bp_month = services_settings.SERVICES_SERVICE_ANUAL_BILLING_MONTH
        if now.month > bp_month:
            bp = datetime.datetime(year=now.year+1, month=bp_month,
                day=1, tzinfo=timezone.get_current_timezone())
        else:
            bp = datetime.datetime(year=now.year, month=bp_month,
                day=1, tzinfo=timezone.get_current_timezone())
        bills = service.orders.bill(billing_point=now, fixed_point=False)
        size = decimal.Decimal((bp - now).days)/365
        error = decimal.Decimal(0.05)
        self.assertGreater(10*size+error*(10*size), bills[0].get_total())
        self.assertLess(10*size-error*(10*size), bills[0].get_total())
