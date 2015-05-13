import decimal
import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from orchestra.contrib.systemusers.models import SystemUser
from orchestra.utils.tests import random_ascii, BaseTestCase

from ... import settings
from ...models import Service


class FTPBillingTest(BaseTestCase):
    DEPENDENCIES = (
        'orchestra.contrib.orders',
        'orchestra.contrib.plans',
        'orchestra.contrib.systemusers',
    )
    
    def create_ftp_service(self):
        return Service.objects.create(
            description="FTP Account",
            content_type=ContentType.objects.get_for_model(SystemUser),
            match='not systemuser.is_main',
            billing_period=Service.ANUAL,
            billing_point=Service.FIXED_DATE,
            is_fee=False,
            metric='',
            pricing_period=Service.NEVER,
            rate_algorithm='orchestra.contrib.plans.ratings.step_price',
            on_cancel=Service.COMPENSATE,
            payment_style=Service.PREPAY,
            tax=0,
            nominal_price=10,
        )
    
    def create_ftp(self, account=None):
        if not account:
            account = self.create_account()
        username = '%s_ftp' % random_ascii(10)
        return SystemUser.objects.create_user(username, account=account)
    
    def test_ftp_account_1_year_fiexed(self):
        service = self.create_ftp_service()
        self.create_ftp()
        self.assertEqual(1, service.orders.count())
        bp = timezone.now().date() + relativedelta(years=1)
        bills = service.orders.bill(billing_point=bp, fixed_point=True)
        self.assertEqual(10, bills[0].get_total())
    
    def test_ftp_account_2_year_fiexed(self):
        service = self.create_ftp_service()
        self.create_ftp()
        bp = timezone.now().date() + relativedelta(years=2)
        bills = service.orders.bill(billing_point=bp, fixed_point=True)
        self.assertEqual(20, bills[0].get_total())
    
    def test_ftp_account_6_month_fixed(self):
        service = self.create_ftp_service()
        self.create_ftp()
        bp = timezone.now().date() + relativedelta(months=6)
        bills = service.orders.bill(billing_point=bp, fixed_point=True)
        self.assertEqual(5, bills[0].get_total())
    
    def test_ftp_account_next_billing_point(self):
        service = self.create_ftp_service()
        self.create_ftp()
        now = timezone.now().date()
        bp_month = settings.SERVICES_SERVICE_ANUAL_BILLING_MONTH
        if now.month > bp_month:
            bp = datetime.date(year=now.year+1, month=bp_month, day=1)
        else:
            bp = datetime.date(year=now.year, month=bp_month, day=1)
        bills = service.orders.bill(billing_point=now, fixed_point=False)
        size = decimal.Decimal((bp - now).days)/365
        error = decimal.Decimal(0.05)
        self.assertGreater(10*size+error*(10*size), bills[0].get_total())
        self.assertLess(10*size-error*(10*size), bills[0].get_total())
    
    def test_ftp_account_with_compensation(self):
        account = self.create_account()
        self.create_ftp_service()
        user = self.create_ftp(account=account)
        first_bp = timezone.now().date() + relativedelta(years=2)
        bills = account.orders.bill(billing_point=first_bp, fixed_point=True)
        self.assertEqual(1, account.orders.active().count())
        user.delete()
        self.assertEqual(0, account.orders.active().count())
        user = self.create_ftp(account=account)
        self.assertEqual(1, account.orders.active().count())
        self.assertEqual(2, account.orders.count())
        bp = timezone.now().date() + relativedelta(years=1)
        bills = account.orders.bill(billing_point=bp, fixed_point=True, new_open=True)
        discount = bills[0].lines.order_by('id')[0].sublines.get()
        self.assertEqual(decimal.Decimal(-20), discount.total)
        order = account.orders.order_by('id').first()
        self.assertEqual(order.cancelled_on, order.billed_until)
        order = account.orders.order_by('-id').first()
        self.assertEqual(first_bp, order.billed_until)
        self.assertEqual(decimal.Decimal(0), bills[0].get_total())
