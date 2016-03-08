import os
import smtplib
import time
import requests
from email.mime.text import MIMEText

from django.conf import settings as djsettings
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse
from selenium.webdriver.support.select import Select

from orchestra.admin.utils import change_url
from orchestra.contrib.domains.models import Domain
from orchestra.contrib.orchestration.models import Server, Route
from orchestra.utils.sys import sshrun
from orchestra.utils.tests import (BaseLiveServerTestCase, random_ascii, snapshot_on_error,
        save_response_on_error)

from ... import backends, settings
from ...models import List


class ListMixin(object):
    MASTER_SERVER = os.environ.get('ORCHESTRA_SLAVE_SERVER', 'localhost')
    DEPENDENCIES = (
        'orchestra.contrib.orchestration',
        'orchestra.contrib.domains',
        'orchestra.contrib.lists',
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
        request_address = "{}-request@{}".format(name, address.split('@')[1])
        self.subscribe(subscribe_address)
        time.sleep(3)
        sshrun(self.MASTER_SERVER,
            'grep -v ":\|^\s\|^$\|-\|\.\|\s" /var/spool/mail/nobody | base64 -d | grep "%s"'
            % request_address, display=False)
    
    def validate_login(self, name, password):
        url = 'http://%s/cgi-bin/mailman/admin/%s' % (settings.LISTS_DEFAULT_DOMAIN, name)
        self.assertEqual(200, requests.post(url, data={'adminpw': password}).status_code)
    
    def validate_delete(self, name):
        context = {
            'name': name,
            'domain': Domain.objects.get().name,
            'virtual_domain': settings.LISTS_VIRTUAL_ALIAS_DOMAINS_PATH,
            'virtual_alias': settings.LISTS_VIRTUAL_ALIAS_PATH,
        }
        self.assertRaises(CommandError, sshrun, self.MASTER_SERVER,
            'grep "\s%(name)s\s*" %(virtual_alias)s' % context, display=False)
        self.assertRaises(CommandError, sshrun, self.MASTER_SERVER,
            'grep "^\s*$(domain)s\s*$" %(virtual_domain)s' % context, display=False)
        self.assertRaises(CommandError, sshrun, self.MASTER_SERVER,
            'list_lists | grep -i "^\s*%(name)s\s"' % context, display=False)
    
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
        backend = backends.MailmanController.get_name()
        Route.objects.create(backend=backend, match=True, host=server)
    
    def test_add(self):
        name = '%s_list' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        admin_email = 'root@test3.orchestra.lan'
        self.add(name, password, admin_email)
        self.validate_add(name)
        self.validate_login(name, password)
        self.addCleanup(self.delete, name)
    
    def test_add_with_address(self):
        name = '%s_list' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        admin_email = 'root@test3.orchestra.lan'
        address_name = '%s_name' % random_ascii(10)
        domain_name = '%sdomain.lan' % random_ascii(10)
        address_domain = Domain.objects.create(name=domain_name, account=self.account)
        self.add(name, password, admin_email, address_name=address_name, address_domain=address_domain)
        self.addCleanup(self.delete, name)
        # Mailman doesn't support changing the address, only the domain
        self.validate_add(name, address="%s@%s" % (address_name, address_domain))
    
    def test_change_password(self):
        name = '%s_list' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        admin_email = 'root@test3.orchestra.lan'
        self.add(name, password, admin_email)
        self.addCleanup(self.delete, name)
        self.validate_login(name, password)
        new_password = '@!?%spppP001' % random_ascii(5)
        self.change_password(name, new_password)
        self.validate_login(name, new_password)
    
    def test_change_domain(self):
        name = '%s_list' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        admin_email = 'root@test3.orchestra.lan'
        address_name = '%s_name' % random_ascii(10)
        domain_name = '%sdomain.lan' % random_ascii(10)
        address_domain = Domain.objects.create(name=domain_name, account=self.account)
        self.add(name, password, admin_email, address_name=address_name, address_domain=address_domain)
        self.addCleanup(self.delete, name)
        # Mailman doesn't support changing the address, only the domain
        domain_name = '%sdomain.lan' % random_ascii(10)
        address_domain = Domain.objects.create(name=domain_name, account=self.account)
        self.update_domain(name, domain_name)
        self.validate_add(name, address="%s@%s" % (address_name, address_domain))
    
    def test_change_address_name(self):
        name = '%s_list' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        admin_email = 'root@test3.orchestra.lan'
        address_name = '%s_name' % random_ascii(10)
        domain_name = '%sdomain.lan' % random_ascii(10)
        address_domain = Domain.objects.create(name=domain_name, account=self.account)
        self.add(name, password, admin_email, address_name=address_name, address_domain=address_domain)
        self.addCleanup(self.delete, name)
        # Mailman doesn't support changing the address, only the domain
        address_name = '%s_name' % random_ascii(10)
        self.update_address_name(name, address_name)
        self.validate_add(name, address="%s@%s" % (address_name, address_domain))
    
    def test_delete(self):
        name = '%s_list' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        admin_email = 'root@test3.orchestra.lan'
        address_name = '%s_name' % random_ascii(10)
        domain_name = '%sdomain.lan' % random_ascii(10)
        address_domain = Domain.objects.create(name=domain_name, account=self.account)
        self.add(name, password, admin_email, address_name=address_name, address_domain=address_domain)
        # Mailman doesn't support changing the address, only the domain
        self.validate_add(name, address="%s@%s" % (address_name, address_domain))
        self.delete(name)
        self.assertRaises(AssertionError, self.validate_login, name, password)
        self.validate_delete(name)


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
                'address_domain': self.rest.domains.retrieve(name=address_domain.name).get(),
            })
        self.rest.lists.create(name=name, password=password, admin_email=admin_email, **extra)
    
    @save_response_on_error
    def delete(self, name):
        self.rest.lists.retrieve(name=name).delete()
    
    @save_response_on_error
    def change_password(self, name, password):
        mail_list = self.rest.lists.retrieve(name=name).get()
        mail_list.set_password(password)
    
    @save_response_on_error
    def update_domain(self, name, domain_name):
        mail_list = self.rest.lists.retrieve(name=name).get()
        domain = self.rest.domains.retrieve(name=domain_name).get()
        mail_list.update(address_domain=domain)
    
    @save_response_on_error
    def update_address_name(self, name, address_name):
        mail_list = self.rest.lists.retrieve(name=name).get()
        mail_list.update(address_name=address_name)


class AdminListMixin(ListMixin):
    def setUp(self):
        super(AdminListMixin, self).setUp()
        self.admin_login()
    
    @snapshot_on_error
    def add(self, name, password, admin_email, address_name=None, address_domain=None):
        url = self.live_server_url + reverse('admin:lists_list_add')
        self.selenium.get(url)
        
        name_field = self.selenium.find_element_by_id('id_name')
        name_field.send_keys(name)
        
        password_field = self.selenium.find_element_by_id('id_password1')
        password_field.send_keys(password)
        password_field = self.selenium.find_element_by_id('id_password2')
        password_field.send_keys(password)
        
        admin_email_field = self.selenium.find_element_by_id('id_admin_email')
        admin_email_field.send_keys(admin_email)
        
        if address_name:
            address_name_field = self.selenium.find_element_by_id('id_address_name')
            address_name_field.send_keys(address_name)
            
            domain = Domain.objects.get(name=address_domain)
            domain_input = self.selenium.find_element_by_id('id_address_domain')
            domain_select = Select(domain_input)
            domain_select.select_by_value(str(domain.pk))
        
        name_field.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    @snapshot_on_error
    def delete(self, name):
        mail_list = List.objects.get(name=name)
        self.admin_delete(mail_list)
    
    @snapshot_on_error
    def change_password(self, name, password):
        mail_list = List.objects.get(name=name)
        self.admin_change_password(mail_list, password)
    
    @snapshot_on_error
    def update_domain(self, name, domain_name):
        mail_list = List.objects.get(name=name)
        url = self.live_server_url + change_url(mail_list)
        self.selenium.get(url)
        
        domain = Domain.objects.get(name=domain_name)
        domain_input = self.selenium.find_element_by_id('id_address_domain')
        domain_select = Select(domain_input)
        domain_select.select_by_value(str(domain.pk))
        
        save = self.selenium.find_element_by_name('_save')
        save.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    @snapshot_on_error
    def update_address_name(self, name, address_name):
        mail_list = List.objects.get(name=name)
        url = self.live_server_url + change_url(mail_list)
        self.selenium.get(url)
        
        address_name_field = self.selenium.find_element_by_id('id_address_name')
        address_name_field.clear()
        address_name_field.send_keys(address_name)
        
        save = self.selenium.find_element_by_name('_save')
        save.submit()
        self.assertNotEqual(url, self.selenium.current_url)


class RESTListTest(RESTListMixin, BaseLiveServerTestCase):
    pass


class AdminListTest(AdminListMixin, BaseLiveServerTestCase):
    pass
