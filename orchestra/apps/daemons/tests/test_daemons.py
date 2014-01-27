from django.db import IntegrityError, transaction
from django.test import TestCase

from ..models import Daemon, Host


class DaemonTests(TestCase):
    def setUp(self):
        self.host = Host.objects.create(name='web.example.com')
        self.host1 = Host.objects.create(name='web1.example.com')
        self.host2 = Host.objects.create(name='web2.example.com')
    
    def test_list_backends(self):
        # TODO count actual, register and compare
        choices = list(Daemon._meta.get_field_by_name('backend')[0]._choices)
        self.assertLess(1, len(choices))
    
    def test_get_instances(self):
        from orchestra.core.backends import ServiceBackend
        
        class TestBackend(ServiceBackend):
            name = 'Daemon'
            verbose_name = 'Daemon'
            models = ['daemons.Daemon',]
        
        Daemon._meta.get_field_by_name('backend')[0]._choices = (
            (backend.name, backend.verbose_name)
                    for backend in ServiceBackend.get_backends())
        
        daemon = Daemon.objects.create(name='WebTest', backend='Daemon')
        daemon.instances.create(host=self.host, router='True')
        self.assertEqual(1, len(Daemon.get_instances(daemon)))
        with transaction.atomic():
            self.assertRaises(IntegrityError, daemon.instances.create,
                    host=self.host, router='True')
        daemon.instances.create(host=self.host1, router='obj.name == "WebTest"')
        self.assertEqual(2, len(Daemon.get_instances(daemon)))
        daemon.instances.create(host=self.host2, router='obj.name == "something else"')
        self.assertEqual(2, len(Daemon.get_instances(daemon)))
