import os
import socket
import time
import textwrap

from django.conf import settings as djsettings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse
import requests
from selenium.webdriver.support.select import Select

from orchestra.apps.accounts.models import Account
from orchestra.apps.domains.models import Domain, Record
from orchestra.apps.domains.backends import Bind9MasterDomainBackend
from orchestra.apps.orchestration.models import Server, Route
from orchestra.apps.resources.models import Resource
from orchestra.apps.webapps.tests.functional_tests.tests import StaticWebAppMixin, RESTWebAppMixin, WebAppMixin, PHPFcidWebAppMixin, PHPFPMWebAppMixin
from orchestra.utils.system import run, sshrun
from orchestra.utils.tests import BaseLiveServerTestCase, random_ascii, snapshot_on_error, save_response_on_error

from ... import backends, settings
from ...models import Website


class WebsiteMixin(WebAppMixin):
    MASTER_SERVER = os.environ.get('ORCHESTRA_MASTER_SERVER', 'localhost')
    MASTER_SERVER_ADDR = socket.gethostbyname(MASTER_SERVER)
    DEPENDENCIES = (
        'orchestra.apps.orchestration',
        'orchestra.apps.domains',
        'orchestra.apps.websites',
        'orchestra.apps.webapps',
        'orchestra.apps.systemusers',
    )
    
    def add_route(self):
        super(WebsiteMixin, self).add_route()
        server = Server.objects.get()
        backend = backends.apache.Apache2Backend.get_name()
        Route.objects.get_or_create(backend=backend, match=True, host=server)
        backend = Bind9MasterDomainBackend.get_name()
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



