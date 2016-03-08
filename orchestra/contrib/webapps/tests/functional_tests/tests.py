import ftplib
import os
from io import StringIO

from django.conf import settings as djsettings

from orchestra.contrib.orchestration.models import Server, Route
from orchestra.contrib.systemusers.backends import SystemUserBackend
from orchestra.utils.tests import BaseLiveServerTestCase, random_ascii, snapshot_on_error, save_response_on_error

from ... import backends


class WebAppMixin(object):
    MASTER_SERVER = os.environ.get('ORCHESTRA_MASTER_SERVER', 'localhost')
    DEPENDENCIES = (
        'orchestra.contrib.orchestration',
        'orchestra.contrib.systemusers',
        'orchestra.contrib.webapps',
    )
    
    def setUp(self):
        super(WebAppMixin, self).setUp()
        self.add_route()
        djsettings.DEBUG = True
    
    def add_route(self):
        server, __ = Server.objects.get_or_create(name=self.MASTER_SERVER)
        backend = SystemUserBackend.get_name()
        Route.objects.get_or_create(backend=backend, match=True, host=server)
        backend = self.backend.get_name()
        match = 'webapp.type == "%s"' % self.type_value
        Route.objects.create(backend=backend, match=match, host=server)
    
    def upload_webapp(self, name):
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
    
    def test_add(self):
        name = '%s_%s_webapp' % (random_ascii(10), self.type_value)
        self.add_webapp(name)
        self.addCleanup(self.delete_webapp, name)
        self.upload_webapp(name)


class StaticWebAppMixin(object):
    backend = backends.static.StaticController
    type_value = 'static'
    token = random_ascii(100)
    page = (
        'index.html',
        '<html>Hello World! %s </html>\n' % token,
        '<html>Hello World! %s </html>\n' % token,
    )


class PHPFcidWebAppMixin(StaticWebAppMixin):
    backend = backends.phpfcgid.PHPFcgidBackend
    type_value = 'php5.2'
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
        systemuser = self.rest.systemusers.retrieve().get()
        systemuser.update(is_active=True)
    
    @save_response_on_error
    def add_webapp(self, name, options=[]):
        self.rest.webapps.create(name=name, type=self.type_value, options=options)
    
    @save_response_on_error
    def delete_webapp(self, name):
        self.rest.webapps.retrieve(name=name).delete()


class AdminWebAppMixin(WebAppMixin):
    def setUp(self):
        super(AdminWebAppMixin, self).setUp()
        self.admin_login()
        # create main user
        self.save_systemuser()
    
    @snapshot_on_error
    def save_systemuser(self):
        url = ''
    
    @snapshot_on_error
    def add(self, name, password, admin_email):
        pass


class StaticRESTWebAppTest(StaticWebAppMixin, RESTWebAppMixin, WebAppMixin, BaseLiveServerTestCase):
    pass


class PHPFcidRESTWebAppTest(PHPFcidWebAppMixin, RESTWebAppMixin, WebAppMixin, BaseLiveServerTestCase):
    pass


class PHPFPMRESTWebAppTest(PHPFPMWebAppMixin, RESTWebAppMixin, WebAppMixin, BaseLiveServerTestCase):
    pass


#class AdminWebAppTest(AdminWebAppMixin, BaseLiveServerTestCase):
#    pass



