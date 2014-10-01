from functools import partial

from django.conf import settings
from django.core.urlresolvers import reverse

from orchestra.apps.accounts.models import Account
from orchestra.apps.orchestration.models import Server, Route
from orchestra.utils.system import run
from orchestra.utils.tests import BaseLiveServerTestCase, random_ascii

from ... import backends


r = partial(run, silent=True, display=False)


class SystemUserMixin(object):
    MASTER_ADDR = 'localhost'
    ACCOUNT_USERNAME = '%s_account' % random_ascii(10)
    DEPENDENCIES = (
        'orchestra.apps.orchestration',
        'orcgestra.apps.systemusers',
    )
    
    def setUp(self):
        super(SystemUserMixin, self).setUp()
        self.add_route()
    
    def add_route(self):
        master = Server.objects.create(name=self.MASTER_ADDR)
        backend = backends.SystemUserBackend.get_name()
        Route.objects.create(backend=backend, match=True, host=master)
    
    def add(self):
        raise NotImplementedError
    
    def delete(self):
        raise NotImplementedError
    
    def update(self):
        raise NotImplementedError
    
    def test_create_systemuser(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(username, password)
        self.addCleanup(partial(self.delete, username))
        self.assertEqual(0, r("id %s" % username).return_code)
        # TODO test group membership and everything
    
    def test_delete_systemuser(self):
        username = '%s_systemuser' % random_ascii(10)
        password = '@!?%sppppP001' % random_ascii(5)
        self.add(username, password)
        self.assertEqual(0, r("id %s" % username).return_code)
        self.delete(username)
        self.assertEqual(1, r("id %s" % username, error_codes=[0,1]).return_code)


class RESTSystemUserMixin(SystemUserMixin):
    def setUp(self):
        super(RESTSystemUserMixin, self).setUp()
        self.rest_login()
    
    def add(self, username, password):
        self.rest.systemusers.create(username=username, password=password)
    
    def delete(self, username):
        user = self.rest.systemusers.retrieve(username=username).get()
        user.delete()
    
    def update(self):
        pass


# TODO
class AdminSystemUserMixin(SystemUserMixin):
    def setUp(self):
        super(AdminSystemUserMixin, self).setUp()
        self.admin_login()
    
    def add(self, username, password):
        pass
    
    def delete(self, username):
        pass
    
    def update(self):
        pass


class RESTSystemUserTest(RESTSystemUserMixin, BaseLiveServerTestCase):
    pass


class AdminSystemUserTest(AdminSystemUserMixin, BaseLiveServerTestCase):
    def test_create_account(self):
        url = self.live_server_url + reverse('admin:accounts_account_add')
        self.selenium.get(url)
        
        account_username = '%s_account' % random_ascii(10)
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys(account_username)
        
        account_password = '@!?%spppP001' % random_ascii(5)
        password = self.selenium.find_element_by_id('id_password1')
        password.send_keys(account_password)
        password = self.selenium.find_element_by_id('id_password2')
        password.send_keys(account_password)
        
        account_email = 'orchestra@orchestra.lan'
        email = self.selenium.find_element_by_id('id_email')
        email.send_keys(account_email)
        
        contact_short_name = random_ascii(10)
        short_name = self.selenium.find_element_by_id('id_contacts-0-short_name')
        short_name.send_keys(contact_short_name)
        
        email = self.selenium.find_element_by_id('id_contacts-0-email')
        email.send_keys(account_email)
        email.submit()
        
        account = Account.objects.get(username=account_username)
        self.addCleanup(account.delete)
        self.assertNotEqual(url, self.selenium.current_url)
        self.assertEqual(0, r("id %s" % account.username).return_code)
