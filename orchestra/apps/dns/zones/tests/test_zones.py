from django.db import IntegrityError, transaction
from django.test import TestCase

from ..models import Zone


class DaemonTests(TestCase):
    def setUp(self):
        self.zone = Zone.objects.create(name='rostrepalid.org', hostmaster='rostre.palid@example.com')
    
    def test_refresh_serial(self):
        serial = self.zone.serial
        self.zone.refresh_serial()
        self.assertEqual(serial+1, self.zone.serial)
    
    def test_formatted_hostmaster(self):
        self.assertEqual('rostre\.palid.example.com', self.zone.formatted_hostmaster)
