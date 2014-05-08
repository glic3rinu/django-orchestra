from django.db import IntegrityError, transaction

from orchestra.utils.tests import BaseTestCase

from .. import operations, backends
from ..models import Route, Server
from ..utils import get_backend_choices


class RouterTests(BaseTestCase):
    def setUp(self):
        self.host = Server.objects.create(name='web.example.com')
        self.host1 = Server.objects.create(name='web1.example.com')
        self.host2 = Server.objects.create(name='web2.example.com')
    
    def test_list_backends(self):
        # TODO count actual, register and compare
        choices = list(Route._meta.get_field_by_name('backend')[0]._choices)
        self.assertLess(1, len(choices))
    
    def test_get_instances(self):
        
        class TestBackend(backends.ServiceBackend):
            verbose_name = 'Route'
            models = ['routes.Route',]
        
        choices = get_backend_choices(backends.ServiceBackend.get_backends())
        Route._meta.get_field_by_name('backend')[0]._choices = choices
        backend = TestBackend.get_name()
        
        route = Route.objects.create(backend=backend, host=self.host,
                match='True')
        operation = operations.Operation(TestBackend, route, 'commit')
        self.assertEqual(1, len(Route.get_servers(operation)))
        
        route = Route.objects.create(backend=backend, host=self.host1,
                match='instance.backend == "TestBackend"')
        operation = operations.Operation(TestBackend, route, 'commit')
        self.assertEqual(2, len(Route.get_servers(operation)))
        
        route = Route.objects.create(backend=backend, host=self.host2,
                match='instance.backend == "something else"')
        operation = operations.Operation(TestBackend, route, 'commit')
        self.assertEqual(2, len(Route.get_servers(operation)))
