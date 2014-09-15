import datetime

from dateutil import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from orchestra.apps.accounts.models import Account
from orchestra.apps.users.models import User
from orchestra.utils.tests import BaseTestCase, random_ascii

from ... import settings, helpers
from ...models import Service, Order


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
#            delayed_billing=Service.NEVER,
            is_fee=False,
            metric='',
            pricing_period=Service.BILLING_PERIOD,
            rate_algorithm=Service.STEP_PRICE,
#            orders_effect=Service.CONCURRENT,
            on_cancel=Service.DISCOUNT,
            payment_style=Service.PREPAY,
#            trial_period=Service.NEVER,
#            refound_period=Service.NEVER,
            tax=21,
            nominal_price=10,
        )
        return service
    
#    def test_ftp_account_1_year_fiexed(self):
#        service = self.create_service()
#        bp = timezone.now().date() + relativedelta.relativedelta(years=1)
#        bills = service.orders.bill(billing_point=bp, fixed_point=True)
#        self.assertEqual(20, bills[0].get_total())
    
    def create_ftp(self):
        username = '%s_ftp' % random_ascii(10)
        account = self.create_account()
        user = User.objects.create_user(username=username, account=account)
        POSIX = user._meta.get_field_by_name('posix')[0].model
        POSIX.objects.create(user=user)
        return user
    
    def atest_get_chunks(self):
        service = self.create_service()
        handler = service.handler
        porders = []
        now = timezone.now().date()
        ct = ContentType.objects.get_for_model(User)
        
        ftp = self.create_ftp()
        order = Order.objects.get(content_type=ct, object_id=ftp.pk)
        porders.append(order)
        end = handler.get_billing_point(order).date()
        chunks = handler.get_chunks(porders, now, end)
        self.assertEqual(1, len(chunks))
        self.assertIn([now, end, []], chunks)
        
        ftp = self.create_ftp()
        order1 = Order.objects.get(content_type=ct, object_id=ftp.pk)
        order1.billed_until = now+datetime.timedelta(days=2)
        porders.append(order1)
        chunks = handler.get_chunks(porders, now, end)
        self.assertEqual(2, len(chunks))
        self.assertIn([order1.registered_on, order1.billed_until, [order1]], chunks)
        self.assertIn([order1.billed_until, end, []], chunks)

        ftp = self.create_ftp()
        order2 = Order.objects.get(content_type=ct, object_id=ftp.pk)
        order2.billed_until = now+datetime.timedelta(days=700)
        porders.append(order2)
        chunks = handler.get_chunks(porders, now, end)
        self.assertEqual(2, len(chunks))
        self.assertIn([order.registered_on, order1.billed_until, [order1, order2]], chunks)
        self.assertIn([order1.billed_until, end, [order2]], chunks)

        ftp = self.create_ftp()
        order3 = Order.objects.get(content_type=ct, object_id=ftp.pk)
        order3.billed_until = now+datetime.timedelta(days=700)
        porders.append(order3)
        chunks = handler.get_chunks(porders, now, end)
        self.assertEqual(2, len(chunks))
        self.assertIn([order.registered_on, order1.billed_until, [order1, order2, order3]], chunks)
        self.assertIn([order1.billed_until, end, [order2, order3]], chunks)
        
        ftp = self.create_ftp()
        order4 = Order.objects.get(content_type=ct, object_id=ftp.pk)
        order4.registered_on = now+datetime.timedelta(days=5)
        order4.billed_until = now+datetime.timedelta(days=10)
        porders.append(order4)
        chunks = handler.get_chunks(porders, now, end)
        self.assertEqual(4, len(chunks))
        self.assertIn([order.registered_on, order1.billed_until, [order1, order2, order3]], chunks)
        self.assertIn([order1.billed_until, order4.registered_on, [order2, order3]], chunks)
        self.assertIn([order4.registered_on, order4.billed_until, [order2, order3, order4]], chunks)
        self.assertIn([order4.billed_until, end, [order2, order3]], chunks)
    
        ftp = self.create_ftp()
        order5 = Order.objects.get(content_type=ct, object_id=ftp.pk)
        order5.registered_on = now+datetime.timedelta(days=700)
        order5.billed_until = now+datetime.timedelta(days=780)
        porders.append(order5)
        chunks = handler.get_chunks(porders, now, end)
        self.assertEqual(4, len(chunks))
        self.assertIn([order.registered_on, order1.billed_until, [order1, order2, order3]], chunks)
        self.assertIn([order1.billed_until, order4.registered_on, [order2, order3]], chunks)
        self.assertIn([order4.registered_on, order4.billed_until, [order2, order3, order4]], chunks)
        self.assertIn([order4.billed_until, end, [order2, order3]], chunks)
    
        ftp = self.create_ftp()
        order6 = Order.objects.get(content_type=ct, object_id=ftp.pk)
        order6.registered_on = now-datetime.timedelta(days=780)
        order6.billed_until = now-datetime.timedelta(days=700)
        porders.append(order6)
        chunks = handler.get_chunks(porders, now, end)
        self.assertEqual(4, len(chunks))
        self.assertIn([order.registered_on, order1.billed_until, [order1, order2, order3]], chunks)
        self.assertIn([order1.billed_until, order4.registered_on, [order2, order3]], chunks)
        self.assertIn([order4.registered_on, order4.billed_until, [order2, order3, order4]], chunks)
        self.assertIn([order4.billed_until, end, [order2, order3]], chunks)
    
    def atest_sort_billed_until_or_registered_on(self):
        service = self.create_service()
        now = timezone.now()
        order = Order(
            service=service,
            registered_on=now,
            billed_until=now+datetime.timedelta(days=200))
        order1 = Order(
            service=service,
            registered_on=now+datetime.timedelta(days=5),
            billed_until=now+datetime.timedelta(days=200))
        order2 = Order(
            service=service,
            registered_on=now+datetime.timedelta(days=6),
            billed_until=now+datetime.timedelta(days=200))
        order3 = Order(
            service=service,
            registered_on=now+datetime.timedelta(days=6),
            billed_until=now+datetime.timedelta(days=201))
        order4 = Order(
            service=service,
            registered_on=now+datetime.timedelta(days=6))
        order5 = Order(
            service=service,
            registered_on=now+datetime.timedelta(days=7))
        order6 = Order(
            service=service,
            registered_on=now+datetime.timedelta(days=8))
        orders = [order3, order, order1, order2, order4, order5, order6]
        self.assertEqual(orders, sorted(orders, cmp=helpers.cmp_billed_until_or_registered_on))
    
    def atest_compensation(self):
        now = timezone.now()
        order = Order(
            description='0',
            registered_on=now,
            billed_until=now+datetime.timedelta(days=220),
            cancelled_on=now+datetime.timedelta(days=100))
        order1 = Order(
            description='1',
            registered_on=now+datetime.timedelta(days=5),
            cancelled_on=now+datetime.timedelta(days=190),
            billed_until=now+datetime.timedelta(days=200))
        order2 = Order(
            description='2',
            registered_on=now+datetime.timedelta(days=6),
            cancelled_on=now+datetime.timedelta(days=200),
            billed_until=now+datetime.timedelta(days=200))
        order3 = Order(
            description='3',
            registered_on=now+datetime.timedelta(days=6),
            billed_until=now+datetime.timedelta(days=200))
        
        tests = []
        order4 = Order(
            description='4',
            registered_on=now+datetime.timedelta(days=6),
            billed_until=now+datetime.timedelta(days=102))
        order4.new_billed_until = now+datetime.timedelta(days=200)
        tests.append([
            [now+datetime.timedelta(days=102), now+datetime.timedelta(days=220), order],
        ])
        order5 = Order(
            description='5',
            registered_on=now+datetime.timedelta(days=7),
            billed_until=now+datetime.timedelta(days=102))
        order5.new_billed_until =  now+datetime.timedelta(days=195)
        tests.append([
            [now+datetime.timedelta(days=190), now+datetime.timedelta(days=200), order1]
        ])
        order6 = Order(
            description='6',
            registered_on=now+datetime.timedelta(days=8))
        order6.new_billed_until = now+datetime.timedelta(days=200)
        tests.append([
            [now+datetime.timedelta(days=100), now+datetime.timedelta(days=102), order],
        ])
        porders = [order3, order, order1, order2, order4, order5, order6]
        porders = sorted(porders, cmp=helpers.cmp_billed_until_or_registered_on)
        service = self.create_service()
        compensations = []
        receivers = []
        for order in porders:
            if order.billed_until and order.cancelled_on and order.cancelled_on < order.billed_until:
                compensations.append(helpers.Interval(order.cancelled_on, order.billed_until, order=order))
            elif hasattr(order, 'new_billed_until') and (not order.billed_until or order.billed_until < order.new_billed_until):
                receivers.append(order)
        for order, test in zip(receivers, tests):
            ini = order.billed_until or order.registered_on
            end = order.cancelled_on or now+datetime.timedelta(days=20000)
            order_interval = helpers.Interval(ini, end)
            (compensations, used_compensations) = helpers.compensate(order_interval, compensations)
            for compensation, test_line in zip(used_compensations, test):
                self.assertEqual(test_line[0], compensation.ini)
                self.assertEqual(test_line[1], compensation.end)
                self.assertEqual(test_line[2], compensation.order)
    
    def get_rates(self, account):
        rates = self.rates.filter(Q(plan__is_default=True) | Q(plan__contracts__account=account)).order_by('plan', 'quantity').select_related('plan').disctinct()
    
    def test_rates(self):
        from ...models import Plan
        import sys
        from decimal import Decimal
        service = self.create_service()
        
        superplan = Plan.objects.create(name='SUPER', allow_multiple=False, is_combinable=True)
        service.rates.create(plan=superplan, quantity=1, price=0)
        service.rates.create(plan=superplan, quantity=3, price=10)
        service.rates.create(plan=superplan, quantity=4, price=9)
        service.rates.create(plan=superplan, quantity=10, price=1)
        account = self.create_account()
        account.plans.create(plan=superplan)
        results = service.get_rates(account)
        results = service.rate_method(results, 30)
        rates = [
            {'price': Decimal('0.00'), 'quantity': 2},
            {'price': Decimal('10.00'), 'quantity': 1},
            {'price': Decimal('9.00'), 'quantity': 6},
            {'price': Decimal('1.00'), 'quantity': 21}
        ]
        for rate, result in zip(rates, results):
            self.assertEqual(rate['price'], result.price)
            self.assertEqual(rate['quantity'], result.quantity)
        
        dupeplan = Plan.objects.create(name='DUPE', allow_multiple=True, is_combinable=True)
        service.rates.create(plan=dupeplan, quantity=1, price=0)
        service.rates.create(plan=dupeplan, quantity=3, price=9)
        results = service.get_rates(account)
        results = service.rate_method(results, 30)
        for rate, result in zip(rates, results):
            self.assertEqual(rate['price'], result.price)
            self.assertEqual(rate['quantity'], result.quantity)
        
        account.plans.create(plan=dupeplan)
        results = service.get_rates(account)
        results = service.rate_method(results, 30)
        rates = [
            {'price': Decimal('0.00'), 'quantity': 4},
            {'price': Decimal('9.00'), 'quantity': 5},
            {'price': Decimal('1.00'), 'quantity': 21},
        ]
        for rate, result in zip(rates, results):
            self.assertEqual(rate['price'], result.price)
            self.assertEqual(rate['quantity'], result.quantity)
        
        hyperplan = Plan.objects.create(name='HYPER', allow_multiple=True, is_combinable=False)
        service.rates.create(plan=hyperplan, quantity=1, price=0)
        service.rates.create(plan=hyperplan, quantity=20, price=5)
        account.plans.create(plan=hyperplan)
        results = service.get_rates(account)
        results = service.rate_method(results, 30)
        rates = [
            {'price': Decimal('0.00'), 'quantity': 19},
            {'price': Decimal('5.00'), 'quantity': 11}
        ]
        for rate, result in zip(rates, results):
            self.assertEqual(rate['price'], result.price)
            self.assertEqual(rate['quantity'], result.quantity)
        hyperplan.is_combinable = True
        hyperplan.save()
        results = service.get_rates(account)
        results = service.rate_method(results, 30)
        rates = [
            {'price': Decimal('0.00'), 'quantity': 23},
            {'price': Decimal('1.00'), 'quantity': 7}
        ]
        for rate, result in zip(rates, results):
            self.assertEqual(rate['price'], result.price)
            self.assertEqual(rate['quantity'], result.quantity)
        
        service.rate_algorithm = service.MATCH_PRICE
        service.save()
        results = service.get_rates(account)
        results = service.rate_method(results, 30)
        self.assertEqual(1, len(results))
        self.assertEqual(Decimal('1.00'), results[0].price)
        self.assertEqual(30, results[0].quantity)
        
        hyperplan.delete()
        results = service.get_rates(account)
        results = service.rate_method(results, 8)
        self.assertEqual(1, len(results))
        self.assertEqual(Decimal('9.00'), results[0].price)
        self.assertEqual(8, results[0].quantity)
        
        superplan.delete()
        results = service.get_rates(account)
        results = service.rate_method(results, 30)
        self.assertEqual(1, len(results))
        self.assertEqual(Decimal('9.00'), results[0].price)
        self.assertEqual(30, results[0].quantity)
        
#    def test_ftp_account_1_year_fiexed(self):
#        service = self.create_service()
#        now = timezone.now().date()etb
#        month = settings.ORDERS_SERVICE_ANUAL_BILLING_MONTH
#        ini = datetime.datetime(year=now.year, month=month,
#                day=1, tzinfo=timezone.get_current_timezone())
#        order = service.orders.all()[0]
#        order.registered_on = ini
#        order.save()
#        bp = ini
#        bills = service.orders.bill(billing_point=bp, fixed_point=False, commit=False)
#        print bills[0][1][0].subtotal
#        print bills
#        bp = ini + relativedelta.relativedelta(months=12)
#        bills = service.orders.bill(billing_point=bp, fixed_point=False, commit=False)
#        print bills[0][1][0].subtotal
#        print bills
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

