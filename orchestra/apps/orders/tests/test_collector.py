from django.conf import settings
from django.core.management import call_command
from django.db.models import loading
from django.test import TestCase

from .models import Root, Related, TwoRelated, ThreeRelated, FourRelated


#class CollectorTests(TestCase):
#    def setUp(self):
#        self.root = Root.objects.create(name='randomname')
#        self.related = Related.objects.create(top=self.root)
#    
#    def _pre_setup(self):
#        # Add the models to the db.
#        self._original_installed_apps = list(settings.INSTALLED_APPS)
#        settings.INSTALLED_APPS += ('orchestra.apps.orders.tests',)
#        loading.cache.loaded = False
#        call_command('syncdb', interactive=False, verbosity=0)
#        super(CollectorTests, self)._pre_setup()
#    
#    def _post_teardown(self):
#        super(CollectorTests, self)._post_teardown()
#        settings.INSTALLED_APPS = self._original_installed_apps
#        loading.cache.loaded = False

#    def test_models(self):
#        self.assertEqual('randomname', self.root.name)
