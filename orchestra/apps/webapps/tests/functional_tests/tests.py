import ftplib
import os
import time
import textwrap
from StringIO import StringIO

from django.conf import settings as djsettings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse
from selenium.webdriver.support.select import Select

from orchestra.apps.accounts.models import Account
from orchestra.apps.domains.models import Domain
from orchestra.apps.orchestration.models import Server, Route
from orchestra.apps.resources.models import Resource
from orchestra.apps.systemusers.backends import SystemUserBackend
from orchestra.utils.system import run, sshrun
from orchestra.utils.tests import BaseLiveServerTestCase, random_ascii, snapshot_on_error, save_response_on_error

from ... import backends, settings
from ...models import WebApp


class WebAppMixin(object):
    MASTER_SERVER = os.environ.get('ORCHESTRA_MASTER_SERVER', 'localhost')
    DEPENDENCIES = (
        'orchestra.apps.orchestration',
        'orchestra.apps.systemusers',
        'orchestra.apps.webapps',
    )
    
    def setUp(self):
        super(WebAppMixin, self).setUp()
        self.add_route()
        djsettings.DEBUG = True
    
    def add_route(self):
#        backends = [
#            # TODO MU apps on SaaS?
#            backends.awstats.AwstatsBackend,
#            backends.dokuwikimu.DokuWikiMuBackend,
#            backends.drupalmu.DrupalMuBackend,
#            backends.phpfcgid.PHPFcgidBackend,
#            backends.phpfpm.PHPFPMBackend,
#            backends.static.StaticBackend,
#            backends.wordpressmu.WordpressMuBackend,
#        ]
        server = Server.objects.create(name=self.MASTER_SERVER)
        for backend in [SystemUserBackend, self.backend]:
            backend = backend.get_name()
            Route.objects.create(backend=backend, match=True, host=server)
    
    def test_add(self):
        name = '%s_%s_webapp' % (random_ascii(10), self.type_value)
        self.add_webapp(name)
        self.validate_add_webapp(name)
#        self.addCleanup(self.delete, username)


class StaticWebAppMixin(object):
    backend = backends.static.StaticBackend
    type_value = 'static'
    token = random_ascii(100)
    page = (
        'index.html',
        '<html>Hello World! %s </html>\n' % token,
        '<html>Hello World! %s </html>\n' % token,
    )
    
    def validate_add_webapp(self, name):
        try:
            ftp = ftplib.FTP(self.MASTER_SERVER)
            ftp.login(user=self.account.username, passwd=self.account_password)
            ftp.cwd('webapps/%s' % name)
            index = StringIO()
            index.write(self.page[1])
            index.seek(0)
            ftp.storbinary('STOR %s' % self.page[0], index)
            index.close()
        finally:
            ftp.close()


class PHPFcidWebAppMixin(StaticWebAppMixin):
    backend = backends.phpfcgid.PHPFcgidBackend
    type_value = 'php5'
    token = random_ascii(100)
    page = (
        'index.php',
        '<?php print("Hello World! %s");\n?>\n' % token,
        'Hello World! %s' % token,
    )


class PHPFPMWebAppMixin(PHPFcidWebAppMixin):
    backend = backends.phpfpm.PHPFPMBackend
    type_value = 'php5.5'


class RESTWebAppMixin(object):
    def setUp(self):
        super(RESTWebAppMixin, self).setUp()
        self.rest_login()
        # create main user
        self.save_systemuser()
    
    @save_response_on_error
    def save_systemuser(self):
        self.rest.systemusers.retrieve().get().save()
    
    @save_response_on_error
    def add_webapp(self, name, options=[]):
        self.rest.webapps.create(name=name, type=self.type_value)
    
    @save_response_on_error
    def delete_webapp(self, name):
        list = self.rest.lists.retrieve(name=name).get()
        list.delete()


class AdminWebAppMixin(WebAppMixin):
    def setUp(self):
        super(AdminWebAppMixin, self).setUp()
        self.admin_login()
        # create main user
        self.save_systemuser()
    # TODO save_account()
    
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


class RESTWebAppTest(StaticWebAppMixin, RESTWebAppMixin, WebAppMixin, BaseLiveServerTestCase):
    pass


class RESTWebAppTest(PHPFcidWebAppMixin, RESTWebAppMixin, WebAppMixin, BaseLiveServerTestCase):
    pass


class RESTWebAppTest(PHPFPMWebAppMixin, RESTWebAppMixin, WebAppMixin, BaseLiveServerTestCase):
    pass


#class AdminWebAppTest(AdminWebAppMixin, BaseLiveServerTestCase):
#    pass



