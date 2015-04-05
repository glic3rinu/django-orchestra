from orchestra.utils.tests import BaseTestCase

from ..models import Domain


class DomainTest(BaseTestCase):
    def test_top_relation(self):
        account = self.create_account()
        domain = Domain.objects.create(name='rostrepalid.org', account=account)
        Domain.objects.create(name='www.rostrepalid.org')
        Domain.objects.create(name='mail.rostrepalid.org')
        self.assertEqual(2, len(domain.subdomains.all()))
    
    def test_render_zone(self):
        account = self.create_account()
        domain = Domain.objects.create(name='rostrepalid.org', account=account)
        domain.render_zone()

