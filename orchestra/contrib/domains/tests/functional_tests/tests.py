import os
import time
import socket
from functools import partial

from django.conf import settings as djsettings
from django.core.urlresolvers import reverse
from selenium.webdriver.support.select import Select

from orchestra.contrib.orchestration.models import Server, Route
from orchestra.utils.tests import BaseLiveServerTestCase, random_ascii, snapshot_on_error, save_response_on_error
from orchestra.utils.sys import run

from ... import settings, utils, backends
from ...models import Domain, Record


run = partial(run, display=False)


class DomainTestMixin(object):
    MASTER_SERVER = os.environ.get('ORCHESTRA_MASTER_SERVER', 'localhost')
    SLAVE_SERVER = os.environ.get('ORCHESTRA_SLAVE_SERVER', 'localhost')
    MASTER_SERVER_ADDR = socket.gethostbyname(MASTER_SERVER)
    SLAVE_SERVER_ADDR = socket.gethostbyname(SLAVE_SERVER)
    
    def setUp(self):
        djsettings.DEBUG = True
        super(DomainTestMixin, self).setUp()
        self.domain_name = 'orchestra%s.lan' % random_ascii(10)
        self.domain_records = (
            (Record.MX, '10 mail.orchestra.lan.'),
            (Record.MX, '20 mail2.orchestra.lan.'),
            (Record.NS, 'ns1.%s.' % self.domain_name),
            (Record.NS, 'ns2.%s.' % self.domain_name),
        )
        self.domain_update_records = (
            (Record.MX, '30 mail3.orchestra.lan.'),
            (Record.MX, '40 mail4.orchestra.lan.'),
            (Record.NS, 'ns1.%s.' % self.domain_name),
            (Record.NS, 'ns2.%s.' % self.domain_name),
        )
        self.ns1_name = 'ns1.%s' % self.domain_name
        self.ns1_records = (
            (Record.A, self.SLAVE_SERVER_ADDR),
        )
        self.ns2_name = 'ns2.%s' % self.domain_name
        self.ns2_records = (
            (Record.A, self.MASTER_SERVER_ADDR),
        )
        self.www_name = 'www.%s' % self.domain_name
        self.www_records = (
            (Record.CNAME, 'external.server.org.'),
        )
        self.django_domain_name = 'django%s.lan' % random_ascii(10)
    
    def add_route(self):
        raise NotImplementedError
    
    def add(self, domain_name, records):
        raise NotImplementedError
    
    def delete(self, domain_name, records):
        raise NotImplementedError
    
    def update(self, domain_name, records):
        raise NotImplementedError
    
    def validate_add(self, server_addr, domain_name):
        context = {
            'domain_name': domain_name,
            'server_addr': server_addr
        }
        dig_soa = 'dig @%(server_addr)s %(domain_name)s SOA|grep "\sSOA\s"'
        soa = run(dig_soa % context).stdout.split()
        # testdomain.org. 3600 IN SOA ns.example.com. hostmaster.example.com. 2014021100 86400 7200 2419200 3600
        self.assertEqual('%(domain_name)s.' % context, soa[0])
        self.assertEqual('3600', soa[1])
        self.assertEqual('IN', soa[2])
        self.assertEqual('SOA', soa[3])
        self.assertEqual('%s.' % settings.DOMAINS_DEFAULT_NAME_SERVER, soa[4])
        hostmaster = utils.format_hostmaster(settings.DOMAINS_DEFAULT_HOSTMASTER)
        self.assertEqual(hostmaster, soa[5])
        
        dig_ns = 'dig @%(server_addr)s %(domain_name)s NS|grep "\sNS\s"'
        name_servers = run(dig_ns % context).stdout
        # testdomain.org. 3600 IN NS ns1.orchestra.lan.
        ns_records = ['ns1.%s.' % self.domain_name, 'ns2.%s.' % self.domain_name]
        self.assertEqual(2, len(name_servers.splitlines()))
        for ns in name_servers.splitlines():
            ns = ns.split()
            # testdomain.org. 3600 IN NS ns1.orchestra.lan.
            self.assertEqual('%(domain_name)s.' % context, ns[0])
            self.assertEqual('3600', ns[1])
            self.assertEqual('IN', ns[2])
            self.assertEqual('NS', ns[3])
            self.assertIn(ns[4], ns_records)
        
        dig_mx = 'dig @%(server_addr)s %(domain_name)s MX|grep "\sMX\s"'
        mail_servers = run(dig_mx % context).stdout
        for mx in mail_servers.splitlines():
            mx = mx.split()
            # testdomain.org. 3600 IN NS ns1.orchestra.lan.
            self.assertEqual('%(domain_name)s.' % context, mx[0])
            self.assertEqual('3600', mx[1])
            self.assertEqual('IN', mx[2])
            self.assertEqual('MX', mx[3])
            self.assertIn(mx[4], ['10', '20'])
            self.assertIn(mx[5], ['mail2.orchestra.lan.', 'mail.orchestra.lan.'])
    
    def validate_delete(self, server_addr, domain_name):
        context = {
            'domain_name': domain_name,
            'server_addr': server_addr
        }
        dig_soa = 'dig @%(server_addr)s %(domain_name)s|grep "\sSOA\s"'
        soa = run(dig_soa % context, valid_codes=(0, 1)).stdout
        if soa:
            soa = soa.split()
            self.assertEqual('IN', soa[2])
            self.assertEqual('SOA', soa[3])
            self.assertNotEqual('%s.' % settings.DOMAINS_DEFAULT_NAME_SERVER, soa[4])
            hostmaster = utils.format_hostmaster(settings.DOMAINS_DEFAULT_HOSTMASTER)
            self.assertNotEqual(hostmaster, soa[5])
    
    def validate_update(self, server_addr, domain_name):
        context = {
            'domain_name': domain_name,
            'server_addr': server_addr
        }
        dig_soa = 'dig @%(server_addr)s %(domain_name)s SOA | grep "\sSOA\s"'
        soa = run(dig_soa % context).stdout.split()
        # testdomain.org. 3600 IN SOA ns.example.com. hostmaster.example.com. 2014021100 86400 7200 2419200 3600
        self.assertEqual('%(domain_name)s.' % context, soa[0])
        self.assertEqual('3600', soa[1])
        self.assertEqual('IN', soa[2])
        self.assertEqual('SOA', soa[3])
        self.assertEqual('%s.' % settings.DOMAINS_DEFAULT_NAME_SERVER, soa[4])
        hostmaster = utils.format_hostmaster(settings.DOMAINS_DEFAULT_HOSTMASTER)
        self.assertEqual(hostmaster, soa[5])
        
        dig_ns = 'dig @%(server_addr)s %(domain_name)s NS  |grep "\sNS\s"'
        name_servers = run(dig_ns % context).stdout
        ns_records = ['ns1.%s.' % self.domain_name, 'ns2.%s.' % self.domain_name]
        self.assertEqual(2, len(name_servers.splitlines()))
        for ns in name_servers.splitlines():
            ns = ns.split()
            # testdomain.org. 3600 IN NS ns1.orchestra.lan.
            self.assertEqual('%(domain_name)s.' % context, ns[0])
            self.assertEqual('3600', ns[1])
            self.assertEqual('IN', ns[2])
            self.assertEqual('NS', ns[3])
            self.assertIn(ns[4], ns_records)
        
        dig_mx = 'dig @%(server_addr)s %(domain_name)s MX | grep "\sMX\s"'
        mx = run(dig_mx % context).stdout.split()
        # testdomain.org. 3600 IN MX 10 orchestra.lan.
        self.assertEqual('%(domain_name)s.' % context, mx[0])
        self.assertEqual('3600', mx[1])
        self.assertEqual('IN', mx[2])
        self.assertEqual('MX', mx[3])
        self.assertIn(mx[4], ['30', '40'])
        self.assertIn(mx[5], ['mail3.orchestra.lan.', 'mail4.orchestra.lan.'])
        
    def validate_www_update(self, server_addr, domain_name):
        context = {
            'domain_name': domain_name,
            'server_addr': server_addr
        }
        dig_cname = 'dig @%(server_addr)s www.%(domain_name)s CNAME | grep "\sCNAME\s"'
        cname = run(dig_cname % context).stdout.split()
        # testdomain.org. 3600 IN MX 10 orchestra.lan.
        self.assertEqual('www.%(domain_name)s.' % context, cname[0])
        self.assertEqual('3600', cname[1])
        self.assertEqual('IN', cname[2])
        self.assertEqual('CNAME', cname[3])
        self.assertEqual('external.server.org.', cname[4])
    
    def test_add(self):
        self.add(self.ns1_name, self.ns1_records)
        self.add(self.ns2_name, self.ns2_records)
        self.add(self.domain_name, self.domain_records)
#        self.addCleanup(self.delete, self.domain_name)
        self.validate_add(self.MASTER_SERVER_ADDR, self.domain_name)
        time.sleep(1)
        self.validate_add(self.SLAVE_SERVER_ADDR, self.domain_name)
    
    def test_delete(self):
        self.add(self.ns1_name, self.ns1_records)
        self.add(self.ns2_name, self.ns2_records)
        self.add(self.domain_name, self.domain_records)
        self.delete(self.domain_name)
        for name in [self.domain_name, self.ns1_name, self.ns2_name]:
            self.validate_delete(self.MASTER_SERVER_ADDR, name)
            self.validate_delete(self.SLAVE_SERVER_ADDR, name)
    
    def test_update(self):
        self.add(self.ns1_name, self.ns1_records)
        self.add(self.ns2_name, self.ns2_records)
        self.add(self.domain_name, self.domain_records)
        self.addCleanup(self.delete, self.domain_name)
        self.update(self.domain_name, self.domain_update_records)
        time.sleep(0.5)
        self.validate_update(self.MASTER_SERVER_ADDR, self.domain_name)
        time.sleep(5)
        self.validate_update(self.SLAVE_SERVER_ADDR, self.domain_name)
        self.add(self.www_name, self.www_records)
        time.sleep(0.5)
        self.validate_www_update(self.MASTER_SERVER_ADDR, self.domain_name)
        time.sleep(5)
        self.validate_www_update(self.SLAVE_SERVER_ADDR, self.domain_name)
    
    def test_add_add_delete_delete(self):
        self.add(self.ns1_name, self.ns1_records)
        self.add(self.ns2_name, self.ns2_records)
        self.add(self.domain_name, self.domain_records)
        self.add(self.django_domain_name, self.domain_records)
        self.delete(self.domain_name)
        self.validate_add(self.MASTER_SERVER_ADDR, self.django_domain_name)
        self.validate_add(self.SLAVE_SERVER_ADDR, self.django_domain_name)
        self.delete(self.django_domain_name)
        self.validate_delete(self.MASTER_SERVER_ADDR, self.django_domain_name)
        self.validate_delete(self.SLAVE_SERVER_ADDR, self.django_domain_name)
    
    def test_bad_creation(self):
        self.assertRaises((self.rest.ResponseStatusError, AssertionError),
                self.add, self.domain_name, self.domain_records)


class AdminDomainMixin(DomainTestMixin):
    def setUp(self):
        super(AdminDomainMixin, self).setUp()
        self.add_route()
        self.admin_login()
    
    def _add_records(self, records):
        self.selenium.find_element_by_link_text('Add another Record').click()
        for i, record in zip(range(0, len(records)), records):
            type, value = record
            type_input = self.selenium.find_element_by_id('id_records-%d-type' % i)
            type_select = Select(type_input)
            type_select.select_by_value(type)
            value_input = self.selenium.find_element_by_id('id_records-%d-value' % i)
            value_input.clear()
            value_input.send_keys(value)
        return value_input
    
    @snapshot_on_error
    def add(self, domain_name, records):
        add = reverse('admin:domains_domain_add')
        url = self.live_server_url + add
        self.selenium.get(url)
        
        name = self.selenium.find_element_by_id('id_name')
        name.send_keys(domain_name)
        
        account_input = self.selenium.find_element_by_id('id_account')
        account_select = Select(account_input)
        account_select.select_by_value(str(self.account.pk))
        
        value_input = self._add_records(records)
        value_input.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    @snapshot_on_error
    def delete(self, domain_name):
        domain = Domain.objects.get(name=domain_name)
        self.admin_delete(domain)
    
    @snapshot_on_error
    def update(self, domain_name, records):
        domain = Domain.objects.get(name=domain_name)
        change = reverse('admin:domains_domain_change', args=(domain.pk,))
        url = self.live_server_url + change
        self.selenium.get(url)
        value_input = self._add_records(records)
        value_input.submit()
        self.assertNotEqual(url, self.selenium.current_url)


class RESTDomainMixin(DomainTestMixin):
    def setUp(self):
        super(RESTDomainMixin, self).setUp()
        self.rest_login()
        self.add_route()
    
    @save_response_on_error
    def add(self, domain_name, records):
        records = [ dict(type=type, value=value) for type,value in records ]
        self.rest.domains.create(name=domain_name, records=records)
    
    @save_response_on_error
    def delete(self, domain_name):
        domain = Domain.objects.get(name=domain_name)
        domain = self.rest.domains.retrieve(id=domain.pk)
        domain.delete()
    
    @save_response_on_error
    def update(self, domain_name, records):
        records = [ dict(type=type, value=value) for type,value in records ]
        domains = self.rest.domains.retrieve(name=domain_name)
        domain = domains.get()
        domain.update(records=records)


class Bind9BackendMixin(object):
    DEPENDENCIES = (
        'orchestra.contrib.orchestration',
    )
    
    def add_route(self):
        master = Server.objects.create(name=self.MASTER_SERVER, address=self.MASTER_SERVER_ADDR)
        backend = backends.Bind9MasterDomainController.get_name()
        Route.objects.create(backend=backend, match=True, host=master)
        slave = Server.objects.create(name=self.SLAVE_SERVER, address=self.SLAVE_SERVER_ADDR)
        backend = backends.Bind9SlaveDomainController.get_name()
        Route.objects.create(backend=backend, match=True, host=slave)


class RESTBind9BackendDomainTest(Bind9BackendMixin, RESTDomainMixin, BaseLiveServerTestCase):
    pass


class AdminBind9BackendDomainTest(Bind9BackendMixin, AdminDomainMixin, BaseLiveServerTestCase):
    pass
