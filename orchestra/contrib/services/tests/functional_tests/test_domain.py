from django.contrib.contenttypes.models import ContentType

from orchestra.contrib.miscellaneous.models import MiscService, Miscellaneous
from orchestra.contrib.plans.models import Plan
from orchestra.utils.tests import random_ascii, BaseTestCase

from ...models import Service


class DomainBillingTest(BaseTestCase):
    def create_domain_service(self):
        service = Service.objects.create(
            description="Domain .ES",
            content_type=ContentType.objects.get_for_model(Miscellaneous),
            match="miscellaneous.is_active and miscellaneous.service.name.lower() == 'domain .es'",
            billing_period=Service.ANUAL,
            billing_point=Service.ON_REGISTER,
            is_fee=False,
            metric='',
            pricing_period=Service.BILLING_PERIOD,
            rate_algorithm='orchestra.contrib.plans.ratings.step_price',
            on_cancel=Service.NOTHING,
            payment_style=Service.PREPAY,
            tax=0,
            nominal_price=10
        )
        plan = Plan.objects.create(is_default=True, name='Default')
        service.rates.create(plan=plan, quantity=0, price=0)
        service.rates.create(plan=plan, quantity=2, price=10)
        service.rates.create(plan=plan, quantity=4, price=9)
        service.rates.create(plan=plan, quantity=6, price=6)
        return service
    
    def create_domain(self, account=None):
        if not account:
            account = self.create_account()
        domain_name = '%s.es' % random_ascii(10)
        domain_service, __ = MiscService.objects.get_or_create(name='domain .es',
                description='Domain .ES')
        return account.miscellaneous.create(service=domain_service, description=domain_name)
    
    def test_domain(self):
        self.create_domain_service()
        account = self.create_account()
        self.create_domain(account=account)
        bills = account.orders.bill()
        self.assertEqual(0, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill()
        self.assertEqual(10, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill()
        self.assertEqual(20, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill()
        self.assertEqual(29, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill()
        self.assertEqual(38, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill()
        self.assertEqual(44, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill()
        self.assertEqual(50, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill()
        self.assertEqual(56, bills[0].get_total())
    
    def test_domain_proforma(self):
        self.create_domain_service()
        account = self.create_account()
        self.create_domain(account=account)
        bills = account.orders.bill(proforma=True, new_open=True)
        self.assertEqual(0, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(proforma=True, new_open=True)
        self.assertEqual(10, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(proforma=True, new_open=True)
        self.assertEqual(20, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(proforma=True, new_open=True)
        self.assertEqual(29, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(proforma=True, new_open=True)
        self.assertEqual(38, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(proforma=True, new_open=True)
        self.assertEqual(44, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(proforma=True, new_open=True)
        self.assertEqual(50, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(proforma=True, new_open=True)
        self.assertEqual(56, bills[0].get_total())
    
    def test_domain_cumulative(self):
        self.create_domain_service()
        account = self.create_account()
        self.create_domain(account=account)
        bills = account.orders.bill(proforma=True)
        self.assertEqual(0, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(proforma=True)
        self.assertEqual(10, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(proforma=True)
        self.assertEqual(30, bills[0].get_total())
    
    def test_domain_new_open(self):
        self.create_domain_service()
        account = self.create_account()
        self.create_domain(account=account)
        bills = account.orders.bill(new_open=True)
        self.assertEqual(0, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(new_open=True)
        self.assertEqual(10, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(new_open=True)
        self.assertEqual(10, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(new_open=True)
        self.assertEqual(9, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(new_open=True)
        self.assertEqual(9, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(new_open=True)
        self.assertEqual(6, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(new_open=True)
        self.assertEqual(6, bills[0].get_total())
        self.create_domain(account=account)
        bills = account.orders.bill(new_open=True)
        self.assertEqual(6, bills[0].get_total())

