import MySQLdb
import os
from functools import partial

from django.conf import settings as djsettings
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse
from selenium.webdriver.support.select import Select

from orchestra.apps.accounts.models import Account
from orchestra.apps.orchestration.models import Server, Route
from orchestra.utils.system import run
from orchestra.utils.tests import (BaseLiveServerTestCase, random_ascii, save_response_on_error,
        snapshot_on_error)

from ... import backends, settings
from ...models import Database


class DatabaseTestMixin(object):
    MASTER_SERVER = os.environ.get('ORCHESTRA_SECOND_SERVER', 'localhost')
    DEPENDENCIES = (
        'orchestra.apps.orchestration',
        'orcgestra.apps.databases',
    )
    
    def setUp(self):
        super(DatabaseTestMixin, self).setUp()
        self.add_route()
        djsettings.DEBUG = True
    
    def add_route(self):
        raise NotImplementedError
    
    def save(self):
        raise NotImplementedError
    
    def add(self):
        raise NotImplementedError
    
    def delete(self):
        raise NotImplementedError
    
    def update(self):
        raise NotImplementedError
    
    def disable(self):
        raise NotImplementedError
    
    def add_group(self, username, groupname):
        raise NotImplementedError
    
    def test_add(self):
        dbname = '%s_database' % random_ascii(5)
        username = '%s_dbuser' % random_ascii(10)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(dbname, username, password)
        self.validate_create_table(dbname, username, password)


class MySQLBackendMixin(object):
    db_type = 'mysql'
    
    def add_route(self):
        server = Server.objects.create(name=self.MASTER_SERVER)
        backend = backends.MySQLBackend.get_name()
        match = "database.type == '%s'" % self.db_type
        Route.objects.create(backend=backend, match=match, host=server)
        match = "databaseuser.type == '%s'" % self.db_type
        backend = backends.MySQLUserBackend.get_name()
        Route.objects.create(backend=backend, match=match, host=server)
    
    def validate_create_table(self, name, username, password):
        db = MySQLdb.connect(host=self.MASTER_SERVER, port=3306, user=username, passwd=password, db=name)
        cur = db.cursor()
        cur.execute('CREATE TABLE test;')
    
    def validate_delete(self, name, username, password):
        self.asseRaises(MySQLdb.ConnectionError,
                self.validate_create_table, name, username, password)



class RESTDatabaseMixin(DatabaseTestMixin):
    def setUp(self):
        super(RESTDatabaseMixin, self).setUp()
        self.rest_login()
    
    @save_response_on_error
    def add(self, dbname, username, password):
        user = self.rest.databaseusers.create(username=username, password=password)
        self.rest.databases.create(name=dbname, user=user, type=self.db_type)


class AdminDatabaseMixin(DatabaseTestMixin):
    def setUp(self):
        super(AdminDatabaseMixin, self).setUp()
        self.admin_login()
    
    @snapshot_on_error
    def add(self, dbname, username, password):
        url = self.live_server_url + reverse('admin:databases_database_add')
        self.selenium.get(url)
        
        type_input = self.selenium.find_element_by_id('id_type')
        type_select = Select(type_input)
        type_select.select_by_value(self.db_type)
        
        name_field = self.selenium.find_element_by_id('id_name')
        name_field.send_keys(dbname)
        
        username_field = self.selenium.find_element_by_id('id_username')
        username_field.send_keys(username)
        
        password_field = self.selenium.find_element_by_id('id_password1')
        password_field.send_keys(password)
        password_field = self.selenium.find_element_by_id('id_password2')
        password_field.send_keys(password)
        
        name_field.submit()
        self.assertNotEqual(url, self.selenium.current_url)


class RESTMysqlDatabaseTest(MySQLBackendMixin, RESTDatabaseMixin, BaseLiveServerTestCase):
    pass


class AdminMysqlDatabaseTest(MySQLBackendMixin, AdminDatabaseMixin, BaseLiveServerTestCase):
    pass
