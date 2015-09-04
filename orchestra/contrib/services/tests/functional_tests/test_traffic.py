from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from freezegun import freeze_time

from orchestra.contrib.accounts.models import Account
from orchestra.contrib.miscellaneous.models import MiscService, Miscellaneous
from orchestra.contrib.plans.models import Plan
from orchestra.contrib.resources.models import Resource, ResourceData, MonitorData
from orchestra.contrib.resources.backends import ServiceMonitor
from orchestra.utils.tests import BaseTestCase

from ...models import Service


class FTPTrafficMonitor(ServiceMonitor):
    model = 'systemusers.SystemUser'


class BaseTrafficBillingTest(BaseTestCase):
    TRAFFIC_METRIC = 'account.resources.traffic.used'
    DEPENDENCIES = ('orchestra.contrib.resources',)
    
    def create_traffic_service(self):
        service = Service.objects.create(
            description="Traffic",
            content_type=ContentType.objects.get_for_model(Account),
            match="account.is_active",
            billing_period=Service.MONTHLY,
            billing_point=Service.FIXED_DATE,
            is_fee=False,
            metric=self.TRAFFIC_METRIC,
            pricing_period=Service.BILLING_PERIOD,
            rate_algorithm='orchestra.contrib.plans.ratings.step_price',
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
        self.resource = Resource.objects.create(
            name='traffic',
            content_type=ContentType.objects.get_for_model(Account),
            aggregation='monthly-sum',
            verbose_name='Account Traffic',
            unit='GB',
            scale='10**9',
            on_demand=True,
            # TODO
            monitors=FTPTrafficMonitor.get_name(),
        )
        return self.resource
    
    def report_traffic(self, account, value):
        MonitorData.objects.create(monitor=FTPTrafficMonitor.get_name(), content_object=account.systemusers.get(), value=value)
        data, __ = ResourceData.objects.get_or_create(account, self.resource)
        data.update()


class TrafficBillingTest(BaseTrafficBillingTest):
    def test_traffic(self):
        self.create_traffic_service()
        self.create_traffic_resource()
        account = self.create_account()
        now = timezone.now()
        
        self.report_traffic(account, 10**9)
        bill = account.orders.bill(commit=False)[0]
        self.assertEqual((account, []), bill)
        self.report_traffic(account, 10**9*9)
        
        with freeze_time(now+relativedelta(months=1)):
            bill = account.orders.bill(proforma=True)[0]
            self.report_traffic(account, 10**10*9)
        self.assertEqual(0, bill.get_total())
        
        with freeze_time(now+relativedelta(months=3)):
            bill = account.orders.bill(proforma=True)[0]
        self.assertEqual((90-10)*10, bill.get_total())
    
    def test_multiple_traffics(self):
        self.create_traffic_service()
        self.create_traffic_resource()
        account1 = self.create_account()
        account2 = self.create_account()
        self.report_traffic(account1, 10**10)
        self.report_traffic(account2, 10**10*5)
        with freeze_time(timezone.now()+relativedelta(months=1)):
            bill1 = account1.orders.bill().pop()
            bill2 = account2.orders.bill().pop()
        self.assertNotEqual(bill1.get_total(), bill2.get_total())


class TrafficPrepayBillingTest(BaseTrafficBillingTest):
    TRAFFIC_METRIC = ("max("
        "(account.resources.traffic.used or 0) - "
            "getattr(account.miscellaneous.filter(is_active=True, service__name='traffic prepay').last(), 'amount', 0)"
        ", 0)"
    )
    
    def create_prepay_service(self):
        service = Service.objects.create(
            description="Traffic prepay",
            content_type=ContentType.objects.get_for_model(Miscellaneous),
            match="miscellaneous.is_active and miscellaneous.service.name.lower() == 'traffic prepay'",
            billing_period=Service.MONTHLY,
            # make sure full months are always paid
            billing_point=Service.ON_REGISTER,
            is_fee=False,
            metric="miscellaneous.amount",
            pricing_period=Service.NEVER,
            rate_algorithm='orchestra.contrib.plans.ratings.step_price',
            on_cancel=Service.NOTHING,
            payment_style=Service.PREPAY,
            tax=0,
            nominal_price=50
        )
        return service
    
    def create_prepay(self, amount, account=None):
        if not account:
            account = self.create_account()
        name = 'traffic prepay'
        service, __ = MiscService.objects.get_or_create(name='traffic prepay',
                description='Traffic prepay', has_amount=True)
        return account.miscellaneous.create(service=service, description=name, amount=amount)
    
    def test_traffic_prepay(self):
        self.create_traffic_service()
        self.create_prepay_service()
        self.create_traffic_resource()
        account = self.create_account()
        now = timezone.now()
        
        self.create_prepay(10, account=account)
        bill = account.orders.bill(proforma=True)[0]
        self.assertEqual(10*50, bill.get_total())
        
        self.report_traffic(account, 10**10)
        with freeze_time(now+relativedelta(months=1)):
            bill = account.orders.bill(proforma=True, new_open=True)[0]
            self.assertEqual(2*10*50 + 0*10, bill.get_total())
        
        # TODO RuntimeWarning: DateTimeField MetricStorage.updated_on received a naive
        self.report_traffic(account, 10**10)
        with freeze_time(now+relativedelta(months=1)):
            bill = account.orders.bill(proforma=True, new_open=True)[0]
        self.assertEqual(2*10*50 + 0*10, bill.get_total())
        
        self.report_traffic(account, 10**10)
        with freeze_time(now+relativedelta(months=1)):
            bill = account.orders.bill(proforma=True, new_open=True)[0]
        self.assertEqual(2*10*50 + (30-10-10)*10, bill.get_total())
        
        with freeze_time(now+relativedelta(months=2)):
            self.report_traffic(account, 10**11)
        with freeze_time(now+relativedelta(months=1)):
            bill = account.orders.bill(proforma=True, new_open=True)[0]
            self.assertEqual(2*10*50 + (30-10-10)*10, bill.get_total())
        
        with freeze_time(now+relativedelta(months=3)):
            bill = account.orders.bill(proforma=True, new_open=True)[0]
        self.assertEqual(4*10*50 +  (30-10-10)*10 + (100-10-10)*10, bill.get_total())

