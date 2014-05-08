from django.db import IntegrityError, transaction
from django.test import TestCase

from ..models import Domain


class DomainTests(TestCase):
    def setUp(self):
        self.domain = Domain.objects.create(name='rostrepalid.org')
        Domain.objects.create(name='www.rostrepalid.org')
        Domain.objects.create(name='mail.rostrepalid.org')
    
    def test_top_relation(self):
        self.assertEqual(2, len(self.domain.subdomains.all()))
    
    def test_render_zone(self):
        print self.domain.render_zone()

