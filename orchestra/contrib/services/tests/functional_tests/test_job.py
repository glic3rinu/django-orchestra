from django.contrib.contenttypes.models import ContentType

from orchestra.contrib.miscellaneous.models import MiscService, Miscellaneous
from orchestra.contrib.plans.models import Plan
from orchestra.utils.tests import random_ascii, BaseTestCase

from ...models import Service


class JobBillingTest(BaseTestCase):
    def create_job_service(self):
        service = Service.objects.create(
            description="Random job",
            content_type=ContentType.objects.get_for_model(Miscellaneous),
            match="miscellaneous.is_active and miscellaneous.service.name.lower() == 'job'",
            billing_period=Service.NEVER,
            billing_point=Service.ON_REGISTER,
            is_fee=False,
            metric='miscellaneous.amount',
            pricing_period=Service.BILLING_PERIOD,
            rate_algorithm='orchestra.contrib.plans.ratings.match_price',
            on_cancel=Service.NOTHING,
            payment_style=Service.POSTPAY,
            tax=0,
            nominal_price=20
        )
        plan = Plan.objects.create(is_default=True, name='Default')
        service.rates.create(plan=plan, quantity=1, price=20)
        service.rates.create(plan=plan, quantity=10, price=15)
        return service
    
    def create_job(self, amount, account=None):
        if not account:
            account = self.create_account()
        description = 'Random Job %s' % random_ascii(10)
        service, __ = MiscService.objects.get_or_create(name='job', has_amount=True)
        return account.miscellaneous.create(service=service, description=description, amount=amount)
    
    def test_job(self):
        self.create_job_service()
        account = self.create_account()
        
        self.create_job(5, account=account)
        bill = account.orders.bill()[0]
        self.assertEqual(5*20, bill.get_total())
        
        self.create_job(100, account=account)
        bill = account.orders.bill(new_open=True)[0]
        self.assertEqual(100*15, bill.get_total())
