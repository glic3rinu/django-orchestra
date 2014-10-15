import MySQLdb
import os
import socket
import time
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
from ...models import Database, DatabaseUser


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
        username = '%s_dbuser' % random_ascii(5)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(dbname, username, password)
        self.validate_create_table(dbname, username, password)
    
    def test_change_password(self):
        dbname = '%s_database' % random_ascii(5)
        username = '%s_dbuser' % random_ascii(5)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(dbname, username, password)
        self.validate_create_table(dbname, username, password)
        new_password = '@!?%spppP001' % random_ascii(5)
        self.change_password(username, new_password)
        self.validate_login_error(dbname, username, password)
        self.validate_create_table(dbname, username, new_password)

    # TODO test add user
    # TODO remove user
    # TODO remove all users

class MySQLBackendMixin(object):
    db_type = 'mysql'
    
    def setUp(self):
        super(MySQLBackendMixin, self).setUp()
        # Get local ip address used to reach self.MASTER_SERVER
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((self.MASTER_SERVER, 22))
        settings.DATABASES_DEFAULT_HOST = s.getsockname()[0]
        s.close()
    
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
        cur.execute('CREATE TABLE %s ( id INT ) ;' % random_ascii(20))
    
    def validate_login_error(self, dbname, username, password):
        self.assertRaises(MySQLdb.OperationalError,
            self.validate_create_table, dbname, username, password)
    
    def validate_delete(self, name, username, password):
        self.asseRaises(MySQLdb.ConnectionError,
                self.validate_create_table, name, username, password)


class RESTDatabaseMixin(DatabaseTestMixin):
    def setUp(self):
        super(RESTDatabaseMixin, self).setUp()
        self.rest_login()
    
    @save_response_on_error
    def add(self, dbname, username, password):
        user = self.rest.databaseusers.create(username=username, password=password, type=self.db_type)
        users = [{
            'username': user.username
        }]
        self.rest.databases.create(name=dbname, users=users, type=self.db_type)
    
    @save_response_on_error
    def change_password(self, username, password):
        user = self.rest.databaseusers.retrieve(username=username).get()
        user.set_password(password)


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
    
    @snapshot_on_error
    def delete(self, dbname):
        db = Database.objects.get(name=dbname)
        self.admin_delete(db)
    
    @snapshot_on_error
    def delete_user(self, username):
        user = DatabaseUser.objects.get(username=username)
        self.admin_delete(user)
    
    @snapshot_on_error
    def change_password(self, username, password):
        user = DatabaseUser.objects.get(username=username)
        self.admin_change_password(user, password)


class RESTMysqlDatabaseTest(MySQLBackendMixin, RESTDatabaseMixin, BaseLiveServerTestCase):
    pass


class AdminMysqlDatabaseTest(MySQLBackendMixin, AdminDatabaseMixin, BaseLiveServerTestCase):
    pass
