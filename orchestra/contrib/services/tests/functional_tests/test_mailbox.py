from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from freezegun import freeze_time

from orchestra.contrib.mailboxes.models import Mailbox
from orchestra.contrib.plans.models import Plan
from orchestra.contrib.resources.models import Resource, ResourceData
from orchestra.utils.tests import random_ascii, BaseTestCase

from ...models import Service


class MailboxBillingTest(BaseTestCase):
    def create_mailbox_service(self):
        service = Service.objects.create(
            description="Mailbox",
            content_type=ContentType.objects.get_for_model(Mailbox),
            match="True",
            billing_period=Service.ANUAL,
            billing_point=Service.FIXED_DATE,
            is_fee=False,
            metric='',
            pricing_period=Service.NEVER,
            rate_algorithm='orchestra.contrib.plans.ratings.step_price',
            on_cancel=Service.COMPENSATE,
            payment_style=Service.PREPAY,
            tax=0,
            nominal_price=10
        )
        plan = Plan.objects.create(is_default=True, name='Default')
        service.rates.create(plan=plan, quantity=1, price=0)
        service.rates.create(plan=plan, quantity=5, price=10)
        return service
    
    def create_mailbox_disk_service(self):
        service = Service.objects.create(
            description="Mailbox disk",
            content_type=ContentType.objects.get_for_model(Mailbox),
            match="True",
            billing_period=Service.ANUAL,
            billing_point=Service.FIXED_DATE,
            is_fee=False,
            metric='max((mailbox.resources.disk.allocated or 0) -1, 0)',
            pricing_period=Service.NEVER,
            rate_algorithm='orchestra.contrib.plans.ratings.step_price',
            on_cancel=Service.DISCOUNT,
            payment_style=Service.PREPAY,
            tax=0,
            nominal_price=10
        )
        plan, __ = Plan.objects.get_or_create(is_default=True, name='Default')
        service.rates.create(plan=plan, quantity=1, price=10)
        return service
    
    def create_disk_resource(self):
        self.resource = Resource.objects.create(
            name='disk',
            content_type=ContentType.objects.get_for_model(Mailbox),
            aggregation='last',
            verbose_name='Mailbox disk',
            unit='GB',
            scale=10**9,
            on_demand=False,
            monitors='MaildirDisk',
        )
        return self.resource
    
    def allocate_disk(self, mailbox, value):
        data, __ = ResourceData.objects.get_or_create(mailbox, self.resource)
        data.allocated = value
        data.save()
    
    def create_mailbox(self, account=None):
        if not account:
            account = self.create_account()
        mailbox_name = '%s@orchestra.lan' % random_ascii(10)
        return Mailbox.objects.create(name=mailbox_name, account=account)
    
    def test_mailbox_size(self):
        service = self.create_mailbox_service()
        disk_service = self.create_mailbox_disk_service()
        self.create_disk_resource()
        account = self.create_account()
        mailbox = self.create_mailbox(account=account)
        self.allocate_disk(mailbox, 10)
        bill = service.orders.bill()[0]
        self.assertEqual(0, bill.get_total())
        bp = timezone.now().date() + relativedelta(years=1)
        bill = disk_service.orders.bill(billing_point=bp, fixed_point=True)[0]
        self.assertEqual(90, bill.get_total())
        mailbox = self.create_mailbox(account=account)
        mailbox = self.create_mailbox(account=account)
        mailbox = self.create_mailbox(account=account)
        mailbox = self.create_mailbox(account=account)
        mailbox = self.create_mailbox(account=account)
        mailbox = self.create_mailbox(account=account)
        bill = service.orders.bill(billing_point=bp, fixed_point=True)[0]
        self.assertEqual(120, bill.get_total())
    
    def test_mailbox_size_with_changes(self):
        service = self.create_mailbox_disk_service()
        self.create_disk_resource()
        account = self.create_account()
        mailbox = self.create_mailbox(account=account)
        now = timezone.now()
        bp = now.date() + relativedelta(years=1)
        options = dict(billing_point=bp, fixed_point=True, proforma=True, new_open=True)
        
        self.allocate_disk(mailbox, 10)
        bill = service.orders.bill(**options).pop()
        self.assertEqual(9*10, bill.get_total())
        
        with freeze_time(now+relativedelta(months=6)):
            self.allocate_disk(mailbox, 20)
            bill = service.orders.bill(**options).pop()
            total = 9*10*0.5 + 19*10*0.5
            self.assertEqual(total, bill.get_total())
        
        with freeze_time(now+relativedelta(months=9)):
            self.allocate_disk(mailbox, 30)
            bill = service.orders.bill(**options).pop()
            total = 9*10*0.5 + 19*10*0.25 + 29*10*0.25
            self.assertEqual(total, bill.get_total())
        
        with freeze_time(now+relativedelta(years=1)):
            self.allocate_disk(mailbox, 10)
            bill = service.orders.bill(**options).pop()
            total = 9*10*0.5 + 19*10*0.25 + 29*10*0.25
            self.assertEqual(total, bill.get_total())
    
    def test_mailbox_with_recharge(self):
        service = self.create_mailbox_disk_service()
        self.create_disk_resource()
        account = self.create_account()
        mailbox = self.create_mailbox(account=account)
        now = timezone.now()
        bp = now.date() + relativedelta(years=1)
        options = dict(billing_point=bp, fixed_point=True)
        
        self.allocate_disk(mailbox, 100)
        bill = service.orders.bill(**options).pop()
        self.assertEqual(99*10, bill.get_total())
        
        with freeze_time(now+relativedelta(months=6)):
            self.allocate_disk(mailbox, 50)
            bills = service.orders.bill(**options)
            self.assertEqual([], bills)
        
        with freeze_time(now+relativedelta(months=6)):
            self.allocate_disk(mailbox, 200)
            bill = service.orders.bill(new_open=True, **options).pop()
            self.assertEqual((199-99)*10*0.5, bill.get_total())
        
        with freeze_time(now+relativedelta(months=6)):
            bills = service.orders.bill(new_open=True, **options)
            self.assertEqual([], bills)
    
    def test_mailbox_second_billing(self):
        service = self.create_mailbox_disk_service()
        self.create_disk_resource()
        account = self.create_account()
        mailbox = self.create_mailbox(account=account)
        now = timezone.now()
        bp = now.date() + relativedelta(years=1)
        options = dict(billing_point=bp, fixed_point=True)
        bills = service.orders.bill(**options)
        
        with freeze_time(now+relativedelta(years=1, months=1)):
            mailbox = self.create_mailbox(account=account)
            alt_now = timezone.now()
            bp = alt_now.date() + relativedelta(years=1)
            options = dict(billing_point=bp, fixed_point=True)
            bills = service.orders.bill(**options)
            print(bills)
