from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from freezegun import freeze_time

from orchestra.apps.mails.models import Mailbox
from orchestra.apps.resources.models import Resource, ResourceData, MonitorData
from orchestra.utils.tests import random_ascii

from ...models import Service, Plan

from . import BaseBillingTest


class MailboxBillingTest(BaseBillingTest):
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
            rate_algorithm=Service.STEP_PRICE,
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
            rate_algorithm=Service.STEP_PRICE,
            on_cancel=Service.DISCOUNT,
            payment_style=Service.PREPAY,
            tax=0,
            nominal_price=10
        )
        plan = Plan.objects.create(is_default=True, name='Default')
        service.rates.create(plan=plan, quantity=1, price=10)
        return service
    
    def create_disk_resource(self):
        self.resource = Resource.objects.create(
            name='disk',
            content_type=ContentType.objects.get_for_model(Mailbox),
            period=Resource.LAST,
            verbose_name='Mailbox disk',
            unit='GB',
            scale=10**9,
            ondemand=False,
            monitors='MaildirDisk',
        )
        return self.resource
    
    def allocate_disk(self, mailbox, value):
        data = ResourceData.get_or_create(mailbox, self.resource)
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

    # TODO recharge missing stuff
