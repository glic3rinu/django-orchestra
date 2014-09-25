from django.contrib.contenttypes.models import ContentType

from orchestra.apps.miscellaneous.models import MiscService, Miscellaneous

from ...models import Service, Plan

from . import BaseBillingTest


class PlanBillingTest(BaseBillingTest):
    def create_plan_service(self):
        service = Service.objects.create(
            description="Association membership fee",
            content_type=ContentType.objects.get_for_model(Miscellaneous),
            match="account.is_active and account.type == 'ASSOCIATION'",
            billing_period=Service.ANUAL,
            billing_point=Service.FIXED_DATE,
            is_fee=True,
            metric='',
            pricing_period=Service.BILLING_PERIOD,
            rate_algorithm=Service.STEP_PRICE,
            on_cancel=Service.DISCOUNT,
            payment_style=Service.PREPAY,
            tax=0,
            nominal_price=20
        )
        return service
    
    def create_plan(self):
        if not account:
            account = self.create_account()
        domain_name = '%s.es' % random_ascii(10)
        domain_service, __ = MiscService.objects.get_or_create(name='domain .es', description='Domain .ES')
        return Miscellaneous.objects.create(service=domain_service, description=domain_name, account=account)
    
    def test_plan(self):
        pass
