import os
import socket

import requests

from orchestra.contrib.domains.models import Domain, Record
from orchestra.contrib.domains.backends import Bind9MasterDomainController
from orchestra.contrib.orchestration.models import Server, Route
from orchestra.contrib.webapps.tests.functional_tests.tests import StaticWebAppMixin, RESTWebAppMixin, WebAppMixin, PHPFcidWebAppMixin, PHPFPMWebAppMixin
from orchestra.utils.tests import BaseLiveServerTestCase, random_ascii, save_response_on_error

from ... import backends


class WebsiteMixin(WebAppMixin):
    MASTER_SERVER = os.environ.get('ORCHESTRA_MASTER_SERVER', 'localhost')
    MASTER_SERVER_ADDR = socket.gethostbyname(MASTER_SERVER)
    DEPENDENCIES = (
        'orchestra.contrib.orchestration',
        'orchestra.contrib.domains',
        'orchestra.contrib.websites',
        'orchestra.contrib.webapps',
        'orchestra.contrib.systemusers',
    )
    
    def add_route(self):
        super(WebsiteMixin, self).add_route()
        server = Server.objects.get()
        backend = backends.apache.Apache2Controller.get_name()
        Route.objects.get_or_create(backend=backend, match=True, host=server)
        backend = Bind9MasterDomainController.get_name()
        Route.objects.get_or_create(backend=backend, match=True, host=server)
    
    def validate_add_website(self, name, domain):
        url = 'http://%s/%s' % (domain.name, self.page[0])
        self.assertEqual(self.page[2], requests.get(url).content)
    
    def test_add(self):
        # TODO domains with "_" bad name!
        domain_name = '%sdomain.lan' % random_ascii(10)
        domain = Domain.objects.create(name=domain_name, account=self.account)
        domain.records.create(type=Record.A, value=self.MASTER_SERVER_ADDR)
        self.save_domain(domain)
        webapp = '%s_%s_webapp' % (random_ascii(10), self.type_value)
        self.add_webapp(webapp)
        self.addCleanup(self.delete_webapp, webapp)
        self.upload_webapp(webapp)
        website = '%s_website' % random_ascii(10)
        self.add_website(website, domain, webapp)
        self.addCleanup(self.delete_website, website)
        self.validate_add_website(website, domain)


class RESTWebsiteMixin(RESTWebAppMixin):
    @save_response_on_error
    def save_domain(self, domain):
        self.rest.domains.retrieve().get().save()
    
    @save_response_on_error
    def add_website(self, name, domain, webapp, path='/'):
        domain = self.rest.domains.retrieve(name=domain).get()
        webapp = self.rest.webapps.retrieve(name=webapp).get()
        contents = [{
            'webapp': webapp,
            'path': path
        }]
        self.rest.websites.create(name=name, domains=[domain], contents=contents)
    
    @save_response_on_error
    def delete_website(self, name):
        self.rest.websites.retrieve(name=name).delete()
    
    @save_response_on_error
    def add_content(self, website, webapp, path):
        website = self.rest.websites.retrieve(name=website).get()
        webapp = self.rest.webapps.retrieve(name=webapp).get()
        website.contents.append({
            'webapp': webapp,
            'path': path,
        })
        website.save()

    # TODO test disable
    # TODO test https (refactor ssl)
    # TODO test php options
    # TODO read php-version /fpm/fcgid
    # TODO max_processes, timeouts, memory...


class StaticRESTWebsiteTest(RESTWebsiteMixin, StaticWebAppMixin, WebsiteMixin, BaseLiveServerTestCase):
    def test_mix_webapps(self):
        domain_name = '%sdomain.lan' % random_ascii(10)
        domain = Domain.objects.create(name=domain_name, account=self.account)
        domain.records.create(type=Record.A, value=self.MASTER_SERVER_ADDR)
        self.save_domain(domain)
        webapp = '%s_%s_webapp' % (random_ascii(10), self.type_value)
        self.add_webapp(webapp)
        self.addCleanup(self.delete_webapp, webapp)
        self.upload_webapp(webapp)
        website = '%s_website' % random_ascii(10)
        self.add_website(website, domain, webapp)
        self.addCleanup(self.delete_website, website)
        self.validate_add_website(website, domain)
        
        self.type_value = PHPFcidWebAppMixin.type_value
        self.backend = PHPFcidWebAppMixin.backend
        self.page = PHPFcidWebAppMixin.page
        self.add_route()
        webapp = '%s_%s_webapp' % (random_ascii(10), self.type_value)
        self.add_webapp(webapp)
        self.addCleanup(self.delete_webapp, webapp)
        self.upload_webapp(webapp)
        path = '/%s' % webapp
        self.add_content(website, webapp, path)
        url = 'http://%s%s/%s' % (domain.name, path, self.page[0])
        self.assertEqual(self.page[2], requests.get(url).content)
        
        self.type_value = PHPFPMWebAppMixin.type_value
        self.backend = PHPFPMWebAppMixin.backend
        self.page = PHPFPMWebAppMixin.page
        self.add_route()
        webapp = '%s_%s_webapp' % (random_ascii(10), self.type_value)
        self.add_webapp(webapp)
        self.addCleanup(self.delete_webapp, webapp)
        self.upload_webapp(webapp)
        path = '/%s' % webapp
        
        self.add_content(website, webapp, path)
        url = 'http://%s%s/%s' % (domain.name, path, self.page[0])
        self.assertEqual(self.page[2], requests.get(url).content)


class PHPFcidRESTWebsiteTest(RESTWebsiteMixin, PHPFcidWebAppMixin, WebsiteMixin, BaseLiveServerTestCase):
    pass


class PHPFPMRESTWebsiteTest(RESTWebsiteMixin, PHPFPMWebAppMixin, WebsiteMixin, BaseLiveServerTestCase):
    pass

#class AdminWebsiteTest(AdminWebsiteMixin, BaseLiveServerTestCase):
#    pass



