import email.utils
import os
import smtplib
import time
import textwrap
from email.mime.text import MIMEText

from django.conf import settings as djsettings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse
from selenium.webdriver.support.select import Select

from orchestra.apps.accounts.models import Account
from orchestra.apps.domains.models import Domain
from orchestra.apps.orchestration.models import Server, Route
from orchestra.apps.resources.models import Resource
from orchestra.utils.system import run, sshrun
from orchestra.utils.tests import BaseLiveServerTestCase, random_ascii, snapshot_on_error, save_response_on_error

from ... import backends, settings
from ...models import List


class ListMixin(object):
    MASTER_SERVER = os.environ.get('ORCHESTRA_SLAVE_SERVER', 'localhost')
    DEPENDENCIES = (
        'orchestra.apps.orchestration',
        'orchestra.apps.domains',
        'orchestra.apps.lists',
    )
    
    def setUp(self):
        super(ListMixin, self).setUp()
        self.add_route()
        djsettings.DEBUG = True
    
    def validate_add(self, name, address=None):
        sshrun(self.MASTER_SERVER, 'list_members %s' % name, display=False)
        if not address:
            address = "%s@%s" % (name, settings.LISTS_DEFAULT_DOMAIN)
        subscribe_address = "{}-subscribe@{}".format(*address.split('@'))
        self.subscribe(subscribe_address)
        time.sleep(2)
        sshrun(self.MASTER_SERVER,
            'grep -v ":\|^\s\|^$\|-\|\.\|\s" /var/spool/mail/nobody | base64 -d | grep "%s"' % address, display=False)
    
    def subscribe(self, subscribe_address):
        msg = MIMEText('')
        msg['To'] = subscribe_address
        msg['From'] = 'root@%s' % self.MASTER_SERVER
        msg['Subject'] = 'subscribe'
        server = smtplib.SMTP(self.MASTER_SERVER, 25)
        try:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        finally:
            server.quit()
    
    def add_route(self):
        server = Server.objects.create(name=self.MASTER_SERVER)
        backend = backends.MailmanBackend.get_name()
        Route.objects.create(backend=backend, match=True, host=server)
    
    def atest_add(self):
        name = '%s_list' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        admin_email = 'root@test3.orchestra.lan'
        self.add(name, password, admin_email)
        self.validate_add(name)
#        self.addCleanup(self.delete, username)
    
    def test_add_with_address(self):
        name = '%s_list' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        print password
        admin_email = 'root@test3.orchestra.lan'
        address_name = '%s_name' % random_ascii(10)
        domain_name = '%sdomain.lan' % random_ascii(10)
        address_domain = Domain.objects.create(name=domain_name, account=self.account)
        self.add(name, password, admin_email, address_name=address_name, address_domain=address_domain)
        self.validate_add(name, address="%s@%s" % (address_name, address_domain))


class RESTListMixin(ListMixin):
    def setUp(self):
        super(RESTListMixin, self).setUp()
        self.rest_login()
    
    @save_response_on_error
    def add(self, name, password, admin_email, address_name=None, address_domain=None):
        extra = {}
        if address_name:
            extra.update({
                'address_name': address_name,
                'address_domain': self.rest.domains.retrieve(name=address_domain.name).get().url,
            })
        self.rest.lists.create(name=name, password=password, admin_email=admin_email, **extra)
    
    @save_response_on_error
    def delete(self, username):
        list = self.rest.lists.retrieve(name=username).get()
        list.delete()


class AdminListMixin(ListMixin):
    def setUp(self):
        super(AdminListMixin, self).setUp()
        self.admin_login()
    
    @snapshot_on_error
    def add(self, name, password, admin_email):
        url = self.live_server_url + reverse('admin:mails_List_add')
        self.selenium.get(url)
        
        account_input = self.selenium.find_element_by_id('id_account')
        account_select = Select(account_input)
        account_select.select_by_value(str(self.account.pk))
        
        name_field = self.selenium.find_element_by_id('id_name')
        name_field.send_keys(username)
        
        password_field = self.selenium.find_element_by_id('id_password1')
        password_field.send_keys(password)
        password_field = self.selenium.find_element_by_id('id_password2')
        password_field.send_keys(password)
        
        if quota is not None:
            quota_id = 'id_resources-resourcedata-content_type-object_id-0-allocated'
            quota_field = self.selenium.find_element_by_id(quota_id)
            quota_field.clear()
            quota_field.send_keys(quota)
        
        if filtering is not None:
            filtering_input = self.selenium.find_element_by_id('id_filtering')
            filtering_select = Select(filtering_input)
            filtering_select.select_by_value("CUSTOM")
            filtering_inline = self.selenium.find_element_by_id('fieldsetcollapser0')
            filtering_inline.click()
            time.sleep(0.5)
            filtering_field = self.selenium.find_element_by_id('id_custom_filtering')
            filtering_field.send_keys(filtering)
        
        name_field.submit()
        self.assertNotEqual(url, self.selenium.current_url)


class RESTListTest(RESTListMixin, BaseLiveServerTestCase):
    pass


#class AdminListTest(AdminListMixin, BaseLiveServerTestCase):
#    pass



