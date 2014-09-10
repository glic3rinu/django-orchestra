import datetime

from dateutil import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from orchestra.apps.accounts.models import Account
from orchestra.apps.users.models import User
from orchestra.utils.tests import BaseTestCase

from ... import settings
from ...models import Service


class OrderTests(BaseTestCase):
    DEPENDENCIES = (
        'orchestra.apps.orders',
        'orchestra.apps.users',
        'orchestra.apps.users.roles.posix',
    )
    
    def create_account(self):
        account = Account.objects.create()
        user = User.objects.create_user(username='rata_palida', account=account)
        account.user = user
        account.save()
        return account
    
    def create_service(self):
        service = Service.objects.create(
            description="FTP Account",
            content_type=ContentType.objects.get_for_model(User),
            match='not user.is_main and user.has_posix()',
            billing_period=Service.ANUAL,
            billing_point=Service.FIXED_DATE,
            delayed_billing=Service.NEVER,
            is_fee=False,
            metric='',
            pricing_period=Service.BILLING_PERIOD,
            rate_algorithm=Service.BEST_PRICE,
            orders_effect=Service.CONCURRENT,
            on_cancel=Service.DISCOUNT,
            payment_style=Service.PREPAY,
            trial_period=Service.NEVER,
            refound_period=Service.NEVER,
            tax=21,
            nominal_price=10,
        )
        service.rates.create(
            plan='',
            quantity=1,
            price=9,
        )
        account = self.create_account()
        user = User.objects.create_user(username='rata_palida_ftp', account=account)
        POSIX = user._meta.get_field_by_name('posix')[0].model
        POSIX.objects.create(user=user)
        return service
    
#    def test_ftp_account_1_year_fiexed(self):
#        service = self.create_service()
#        bp = timezone.now().date() + relativedelta.relativedelta(years=1)
#        bills = service.orders.bill(billing_point=bp, fixed_point=True)
#        self.assertEqual(20, bills[0].get_total())

    def test_ftp_account_1_year_fiexed(self):
        service = self.create_service()
        now = timezone.now().date()
        month = settings.ORDERS_SERVICE_ANUAL_BILLING_MONTH
        ini = datetime.datetime(year=now.year, month=month,
                day=1, tzinfo=timezone.get_current_timezone())
        order = service.orders.all()[0]
        order.registered_on = ini
        order.save()
        bp = ini
        bills = service.orders.bill(billing_point=bp, fixed_point=False, commit=False)
        print bills[0][1][0].subtotal
        print bills
        bp = ini + relativedelta.relativedelta(months=12)
        bills = service.orders.bill(billing_point=bp, fixed_point=False, commit=False)
        print bills[0][1][0].subtotal
        print bills
#    def test_ftp_account_2_year_fiexed(self):
#        service = self.create_service()
#        bp = timezone.now().date() + relativedelta.relativedelta(years=2)
#        bills = service.orders.bill(billing_point=bp, fixed_point=True)
#        self.assertEqual(40, bills[0].get_total())
#    
#    def test_ftp_account_6_month_fixed(self):
#        service = self.create_service()
#        bp = timezone.now().date() + relativedelta.relativedelta(months=6)
#        bills = service.orders.bill(billing_point=bp, fixed_point=True)
#        self.assertEqual(6, bills[0].get_total())
#    
#    def test_ftp_account_next_billing_point(self):
#        service = self.create_service()
#        now = timezone.now().date()
#        bp_month = settings.ORDERS_SERVICE_ANUAL_BILLING_MONTH
#        if date.month > bp_month:
#            bp = datetime.datetime(year=now.year+1, month=bp_month,
#                day=1, tzinfo=timezone.get_current_timezone())
#        else:
#            bp = datetime.datetime(year=now.year, month=bp_month,
#                day=1, tzinfo=timezone.get_current_timezone())
#        
#        days = (bp - now).days
#        bills = service.orders.bill(billing_point=bp, fixed_point=False)
#        self.assertEqual(40, bills[0].get_total())

