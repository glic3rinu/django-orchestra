from orchestra.utils.tests import BaseTestCase

from .. import backends, Operation
from ..models import Route, Server


class RouterTests(BaseTestCase):
    def setUp(self):
        self.host = Server.objects.create(name='web.example.com')
        self.host1 = Server.objects.create(name='web1.example.com')
        self.host2 = Server.objects.create(name='web2.example.com')
    
    def test_list_backends(self):
        # TODO count actual, register and compare
        choices = list(Route._meta.get_field('backend')._choices)
        self.assertLess(1, len(choices))
    
    def test_get_instances(self):
        
        class TestBackend(backends.ServiceController):
            verbose_name = 'Route'
            models = ['routes.Route']
            
            def save(self, instance):
                pass
        
        choices = backends.ServiceBackend.get_choices()
        Route._meta.get_field('backend')._choices = choices
        backend = TestBackend.get_name()
        
        route = Route.objects.create(backend=backend, host=self.host, match='True')
        operation = Operation(backend=TestBackend, instance=route, action='save')
        self.assertEqual(1, len(Route.objects.get_for_operation(operation)))

        route = Route.objects.create(backend=backend, host=self.host1,
                match='route.backend == "%s"' % TestBackend.get_name())
        self.assertEqual(2, len(Route.objects.get_for_operation(operation)))
        
        route = Route.objects.create(backend=backend, host=self.host2,
                match='route.backend == "something else"')
        self.assertEqual(2, len(Route.objects.get_for_operation(operation)))
