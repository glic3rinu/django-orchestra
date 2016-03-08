import MySQLdb
import os
import socket
import time

from django.conf import settings as djsettings
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse
from selenium.webdriver.support.select import Select

from orchestra.admin.utils import change_url
from orchestra.contrib.orchestration.models import Server, Route
from orchestra.utils.sys import sshrun
from orchestra.utils.tests import (BaseLiveServerTestCase, random_ascii, save_response_on_error,
        snapshot_on_error)

from ... import backends, settings
from ...models import Database, DatabaseUser


class DatabaseTestMixin(object):
    MASTER_SERVER = os.environ.get('ORCHESTRA_SECOND_SERVER', 'localhost')
    DEPENDENCIES = (
        'orchestra.contrib.orchestration',
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
    
    def test_delete(self):
        dbname = '%s_database' % random_ascii(5)
        username = '%s_dbuser' % random_ascii(5)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(dbname, username, password)
        self.validate_create_table(dbname, username, password)
        self.delete(dbname)
        self.delete_user(username)
        self.validate_delete(dbname, username, password)
        self.validate_delete_user(dbname, username)
    
    def test_change_password(self):
        dbname = '%s_database' % random_ascii(5)
        username = '%s_dbuser' % random_ascii(5)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(dbname, username, password)
        self.addCleanup(self.delete, dbname)
        self.addCleanup(self.delete_user, username)
        self.validate_create_table(dbname, username, password)
        new_password = '@!?%spppP001' % random_ascii(5)
        self.change_password(username, new_password)
        self.validate_login_error(dbname, username, password)
        self.validate_create_table(dbname, username, new_password)
    
    def test_add_user(self):
        dbname = '%s_database' % random_ascii(5)
        username = '%s_dbuser' % random_ascii(5)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(dbname, username, password)
        self.addCleanup(self.delete, dbname)
        self.addCleanup(self.delete_user, username)
        self.validate_create_table(dbname, username, password)
        username2 = '%s_dbuser' % random_ascii(5)
        password2 = '@!?%spppP001' % random_ascii(5)
        self.add_user(username2, password2)
        self.addCleanup(self.delete_user, username2)
        self.validate_login_error(dbname, username2, password2)
        self.add_user_to_db(username2, dbname)
        self.validate_create_table(dbname, username, password)
        self.validate_create_table(dbname, username2, password2)
    
    def test_delete_user(self):
        dbname = '%s_database' % random_ascii(5)
        username = '%s_dbuser' % random_ascii(5)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(dbname, username, password)
        self.addCleanup(self.delete, dbname)
        self.validate_create_table(dbname, username, password)
        username2 = '%s_dbuser' % random_ascii(5)
        password2 = '@!?%spppP001' % random_ascii(5)
        self.add_user(username2, password2)
        self.add_user_to_db(username2, dbname)
        self.delete_user(username)
        self.validate_delete_user(username, password)
        self.validate_login_error(dbname, username, password)
        self.validate_create_table(dbname, username2, password2)
        self.delete_user(username2)
        self.validate_login_error(dbname, username2, password2)
        self.validate_delete_user(username2, password2)
    
    def test_swap_user(self):
        dbname = '%s_database' % random_ascii(5)
        username = '%s_dbuser' % random_ascii(5)
        password = '@!?%spppP001' % random_ascii(5)
        self.add(dbname, username, password)
        self.addCleanup(self.delete, dbname)
        self.addCleanup(self.delete_user, username)
        self.validate_create_table(dbname, username, password)
        username2 = '%s_dbuser' % random_ascii(5)
        password2 = '@!?%spppP001' % random_ascii(5)
        self.add_user(username2, password2)
        self.addCleanup(self.delete_user, username2)
        self.swap_user(username, username2, dbname)
        self.validate_login_error(dbname, username, password)
        self.validate_create_table(dbname, username2, password2)


class MySQLControllerMixin(object):
    db_type = 'mysql'
    
    def setUp(self):
        super(MySQLControllerMixin, self).setUp()
        # Get local ip address used to reach self.MASTER_SERVER
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((self.MASTER_SERVER, 22))
        settings.DATABASES_DEFAULT_HOST = s.getsockname()[0]
        s.close()
    
    def add_route(self):
        server = Server.objects.create(name=self.MASTER_SERVER)
        backend = backends.MySQLController.get_name()
        match = "database.type == '%s'" % self.db_type
        Route.objects.create(backend=backend, match=match, host=server)
        match = "databaseuser.type == '%s'" % self.db_type
        backend = backends.MySQLUserController.get_name()
        Route.objects.create(backend=backend, match=match, host=server)
    
    def validate_create_table(self, name, username, password):
        db = MySQLdb.connect(host=self.MASTER_SERVER, port=3306, user=username, passwd=password, db=name)
        cur = db.cursor()
        cur.execute('CREATE TABLE table_%s ( id INT ) ;' % random_ascii(10))
    
    def validate_login_error(self, dbname, username, password):
        self.assertRaises(MySQLdb.OperationalError,
            self.validate_create_table, dbname, username, password
        )
    
    def validate_delete(self, dbname, username, password):
        self.validate_login_error(dbname, username, password)
        self.assertRaises(CommandError,
            sshrun, self.MASTER_SERVER, 'mysql %s' % dbname, display=False)
    
    def validate_delete_user(self, name, username):
        context = {
            'name': name,
            'username': username,
        }
        self.assertEqual('', sshrun(self.MASTER_SERVER,
            """mysql mysql -e 'SELECT * FROM db WHERE db="%(name)s";'""" % context, display=False).stdout)
        self.assertEqual('', sshrun(self.MASTER_SERVER,
            """mysql mysql -e 'SELECT * FROM user WHERE user="%(username)s";'""" % context, display=False).stdout)


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
    def delete(self, dbname):
        self.rest.databases.retrieve(name=dbname).delete()
    
    @save_response_on_error
    def change_password(self, username, password):
        user = self.rest.databaseusers.retrieve(username=username).get()
        user.set_password(password)
    
    @save_response_on_error
    def add_user(self, username, password):
        self.rest.databaseusers.create(username=username, password=password, type=self.db_type)
    
    @save_response_on_error
    def add_user_to_db(self, username, dbname):
        user = self.rest.databaseusers.retrieve(username=username).get()
        db = self.rest.databases.retrieve(name=dbname).get()
        db.users.append(user)
        db.save()
    
    @save_response_on_error
    def delete_user(self, username):
        self.rest.databaseusers.retrieve(username=username).delete()
    
    @save_response_on_error
    def swap_user(self, username, username2, dbname):
        user = self.rest.databaseusers.retrieve(username=username2).get()
        db = self.rest.databases.retrieve(name=dbname).get()
        db.users = db.users.exclude(username=username)
        db.users.append(user)
        db.save()


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
    def change_password(self, username, password):
        user = DatabaseUser.objects.get(username=username)
        self.admin_change_password(user, password)
    
    @snapshot_on_error
    def add_user(self, username, password):
        url = self.live_server_url + reverse('admin:databases_databaseuser_add')
        self.selenium.get(url)
        
        type_input = self.selenium.find_element_by_id('id_type')
        type_select = Select(type_input)
        type_select.select_by_value(self.db_type)
        
        username_field = self.selenium.find_element_by_id('id_username')
        username_field.send_keys(username)
        
        password_field = self.selenium.find_element_by_id('id_password1')
        password_field.send_keys(password)
        password_field = self.selenium.find_element_by_id('id_password2')
        password_field.send_keys(password)
        
        username_field.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    @snapshot_on_error
    def add_user_to_db(self, username, dbname):
        database = Database.objects.get(name=dbname, type=self.db_type)
        url = self.live_server_url + change_url(database)
        self.selenium.get(url)
        
        user = DatabaseUser.objects.get(username=username, type=self.db_type)
        users_from = self.selenium.find_element_by_id('id_users_from')
        users_select = Select(users_from)
        users_select.select_by_value(str(user.pk))
        
        add_user = self.selenium.find_element_by_id('id_users_add_link')
        add_user.click()
        
        save = self.selenium.find_element_by_name('_save')
        save.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    @snapshot_on_error
    def swap_user(self, username, username2, dbname):
        database = Database.objects.get(name=dbname, type=self.db_type)
        url = self.live_server_url + change_url(database)
        self.selenium.get(url)
        
        # remove user "username"
        user = DatabaseUser.objects.get(username=username, type=self.db_type)
        users_to = self.selenium.find_element_by_id('id_users_to')
        users_select = Select(users_to)
        users_select.select_by_value(str(user.pk))
        remove_user = self.selenium.find_element_by_id('id_users_remove_link')
        remove_user.click()
        time.sleep(0.2)
        
        # add user "username2"
        user = DatabaseUser.objects.get(username=username2, type=self.db_type)
        users_from = self.selenium.find_element_by_id('id_users_from')
        users_select = Select(users_from)
        users_select.select_by_value(str(user.pk))
        add_user = self.selenium.find_element_by_id('id_users_add_link')
        add_user.click()
        time.sleep(0.2)
        
        save = self.selenium.find_element_by_name('_save')
        save.submit()
        self.assertNotEqual(url, self.selenium.current_url)
    
    @snapshot_on_error
    def delete_user(self, username):
        user = DatabaseUser.objects.get(username=username)
        self.admin_delete(user)


class RESTMysqlDatabaseTest(MySQLControllerMixin, RESTDatabaseMixin, BaseLiveServerTestCase):
    pass


class AdminMysqlDatabaseTest(MySQLControllerMixin, AdminDatabaseMixin, BaseLiveServerTestCase):
    pass
