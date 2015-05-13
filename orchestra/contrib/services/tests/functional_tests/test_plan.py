from django.contrib.contenttypes.models import ContentType

from orchestra.contrib.plans.models import Plan, ContractedPlan
from orchestra.utils.tests import BaseTestCase

from ...models import Service


class PlanBillingTest(BaseTestCase):
    def create_plan_service(self):
        service = Service.objects.create(
            description="Association membership fee",
            content_type=ContentType.objects.get_for_model(ContractedPlan),
            match="contractedplan.plan.name == 'association_fee'",
            billing_period=Service.ANUAL,
            billing_point=Service.FIXED_DATE,
            is_fee=True,
            metric='',
            pricing_period=Service.BILLING_PERIOD,
            rate_algorithm='orchestra.contrib.plans.ratings.step_price',
            on_cancel=Service.DISCOUNT,
            payment_style=Service.PREPAY,
            tax=0,
            nominal_price=20
        )
        return service
    
    def create_plan(self, account=None):
        if not account:
            account = self.create_account()
        plan, __ = Plan.objects.get_or_create(name='association_fee')
        return plan.contracts.create(account=account)
    
    def test_update_orders(self):
        account = self.create_account()
        account1 = self.create_account()
        self.create_plan(account=account)
        self.create_plan(account=account1)
        service = self.create_plan_service()
        self.assertEqual(0, service.orders.count())
        service.update_orders()
        self.assertEqual(2, service.orders.count())
    
    def test_plan(self):
        account = self.create_account()
        self.create_plan_service()
        self.create_plan(account=account)
        bill = account.orders.bill().pop()
        self.assertEqual(bill.FEE, bill.type)


# TODO test price with multiple plans
