import datetime
import decimal
import sys

from dateutil import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.utils import timezone

from orchestra.apps.accounts.models import Account
from orchestra.apps.services.models import Service, Plan
from orchestra.apps.services import settings as services_settings
from orchestra.apps.users.models import User
from orchestra.utils.tests import BaseTestCase, random_ascii


class BaseBillingTest(BaseTestCase):
    def create_account(self):
        account = Account.objects.create()
        user = User.objects.create_user(username='rata_palida', account=account)
        account.user = user
        account.save()
        return account


class FTPBillingTest(BaseBillingTest):
    def create_ftp_service(self):
        return Service.objects.create(
            description="FTP Account",
            content_type=ContentType.objects.get_for_model(User),
            match='not user.is_main and user.has_posix()',
            billing_period=Service.ANUAL,
            billing_point=Service.FIXED_DATE,
            is_fee=False,
            metric='',
            pricing_period=Service.NEVER,
            rate_algorithm=Service.STEP_PRICE,
            on_cancel=Service.DISCOUNT,
            payment_style=Service.PREPAY,
            tax=0,
            nominal_price=10,
        )
    
    def create_ftp(self, account=None):
        if not account:
            account = self.create_account()
        username = '%s_ftp' % random_ascii(10)
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
    
    def test_ftp_account_with_compensation(self):
        account = self.create_account()
        service = self.create_ftp_service()
        user = self.create_ftp(account=account)
        first_bp = timezone.now().date() + relativedelta.relativedelta(years=2)
        bills = service.orders.bill(billing_point=first_bp, fixed_point=True)
        self.assertEqual(1, service.orders.active().count())
        user.delete()
        self.assertEqual(0, service.orders.active().count())
        user = self.create_ftp(account=account)
        self.assertEqual(1, service.orders.active().count())
        self.assertEqual(2, service.orders.count())
        bp = timezone.now().date() + relativedelta.relativedelta(years=1)
        bills = service.orders.bill(billing_point=bp, fixed_point=True, new_open=True)
        discount = bills[0].lines.order_by('id')[0].sublines.get()
        self.assertEqual(decimal.Decimal(-20), discount.total)
        order = service.orders.order_by('id').first()
        self.assertEqual(order.cancelled_on, order.billed_until)
        order = service.orders.order_by('-id').first()
        self.assertEqual(first_bp, order.billed_until)
        self.assertEqual(decimal.Decimal(0), bills[0].get_total())

class DomainBillingTest(BaseBillingTest):
    def create_domain_service(self):
        from orchestra.apps.miscellaneous.models import MiscService, Miscellaneous
        service = Service.objects.create(
            description="Domain .ES",
            content_type=ContentType.objects.get_for_model(Miscellaneous),
            match="miscellaneous.is_active and miscellaneous.service.name.lower() == 'domain .es'",
            billing_period=Service.ANUAL,
            billing_point=Service.ON_REGISTER,
            is_fee=False,
            metric='',
            pricing_period=Service.BILLING_PERIOD,
            rate_algorithm=Service.STEP_PRICE,
            on_cancel=Service.NOTHING,
            payment_style=Service.PREPAY,
            tax=0,
            nominal_price=10
        )
        plan = Plan.objects.create(is_default=True, name='Default')
        service.rates.create(plan=plan, quantity=1, price=0)
        service.rates.create(plan=plan, quantity=2, price=10)
        service.rates.create(plan=plan, quantity=4, price=9)
        service.rates.create(plan=plan, quantity=6, price=6)
        return service
    
    def create_domain(self, account=None):
        from orchestra.apps.miscellaneous.models import MiscService, Miscellaneous
        if not account:
            account = self.create_account()
        domain_name = '%s.es' % random_ascii(10)
        domain_service, __ = MiscService.objects.get_or_create(name='domain .es', description='Domain .ES')
        return Miscellaneous.objects.create(service=domain_service, description=domain_name, account=account)
    
    def test_domain(self):
        service = self.create_domain_service()
        account = self.create_account()
        self.create_domain(account=account)
        bills = service.orders.bill()
        self.assertEqual(0, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill()
        self.assertEqual(10, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill()
        self.assertEqual(20, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill()
        self.assertEqual(29, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill()
        self.assertEqual(38, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill()
        self.assertEqual(44, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill()
        self.assertEqual(50, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill()
        self.assertEqual(56, bills[0].get_total())
    
    def test_domain_proforma(self):
        service = self.create_domain_service()
        account = self.create_account()
        self.create_domain(account=account)
        bills = service.orders.bill(proforma=True, new_open=True)
        self.assertEqual(0, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(proforma=True, new_open=True)
        self.assertEqual(10, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(proforma=True, new_open=True)
        self.assertEqual(20, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(proforma=True, new_open=True)
        self.assertEqual(29, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(proforma=True, new_open=True)
        self.assertEqual(38, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(proforma=True, new_open=True)
        self.assertEqual(44, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(proforma=True, new_open=True)
        self.assertEqual(50, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(proforma=True, new_open=True)
        self.assertEqual(56, bills[0].get_total())
    
    def test_domain_cumulative(self):
        service = self.create_domain_service()
        account = self.create_account()
        self.create_domain(account=account)
        bills = service.orders.bill(proforma=True)
        self.assertEqual(0, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(proforma=True)
        self.assertEqual(10, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(proforma=True)
        self.assertEqual(30, bills[0].get_total())
    
    def test_domain_new_open(self):
        service = self.create_domain_service()
        account = self.create_account()
        self.create_domain(account=account)
        bills = service.orders.bill(new_open=True)
        self.assertEqual(0, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(new_open=True)
        self.assertEqual(10, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(new_open=True)
        self.assertEqual(10, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(new_open=True)
        self.assertEqual(9, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(new_open=True)
        self.assertEqual(9, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(new_open=True)
        self.assertEqual(6, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(new_open=True)
        self.assertEqual(6, bills[0].get_total())
        self.create_domain(account=account)
        bills = service.orders.bill(new_open=True)
        self.assertEqual(6, bills[0].get_total())


class TrafficBillingTest(BaseBillingTest):
    def create_traffic_service(self):
        service = Service.objects.create(
            description="Traffic",
            content_type=ContentType.objects.get_for_model(Account),
            match="account.is_active",
            billing_period=Service.MONTHLY,
            billing_point=Service.FIXED_DATE,
            is_fee=False,
            metric='account.resources.traffic.used',
            pricing_period=Service.BILLING_PERIOD,
            rate_algorithm=Service.STEP_PRICE,
            on_cancel=Service.NOTHING,
            payment_style=Service.POSTPAY,
            tax=0,
            nominal_price=10
        )
        plan = Plan.objects.create(is_default=True, name='Default')
        service.rates.create(plan=plan, quantity=1, price=0)
        service.rates.create(plan=plan, quantity=11, price=10)
        return service
    
    def create_traffic_resource(self):
        from orchestra.apps.resources.models import Resource
        self.resource = Resource.objects.create(
            name='traffic',
            content_type=ContentType.objects.get_for_model(Account),
            period=Resource.MONTHLY_SUM,
            verbose_name='Account Traffic',
            unit='GB',
            scale=10**9,
            ondemand=True,
            monitors='FTPTraffic',
        )
        return self.resource
    
    def report_traffic(self, account, date, value):
        from orchestra.apps.resources.models import ResourceData, MonitorData
        ct = ContentType.objects.get_for_model(Account)
        object_id = account.pk
        MonitorData.objects.create(monitor='FTPTraffic', content_object=account.user, value=value, date=date)
        data = ResourceData.get_or_create(account, self.resource)
        data.update()
    
    def test_traffic(self):
        service = self.create_traffic_service()
        resource = self.create_traffic_resource()
        account = self.create_account()
        
        self.report_traffic(account, timezone.now(), 10**9)
        bills = service.orders.bill(commit=False)
        self.assertEqual([(account, [])], bills)
        
        # Prepay
        delta = datetime.timedelta(days=60)
        date = (timezone.now()-delta).date()
        order = service.orders.get()
        order.registered_on = date
        order.save()
        
        self.report_traffic(account, date, 10**9*9)
        order.metrics.update(updated_on=F('updated_on')-delta)
        bills = service.orders.bill(proforma=True)
        self.assertEqual(0, bills[0].get_total())
        
        self.report_traffic(account, date, 10**10*9)
        order.metrics.filter(id=3).update(updated_on=F('updated_on')-delta)
        bills = service.orders.bill(proforma=True)
        self.assertEqual(900, bills[0].get_total())
