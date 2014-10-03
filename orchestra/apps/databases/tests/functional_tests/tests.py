import MySQLdb
from functools import partial

from django.conf import settings as djsettings
from django.core.management.base import CommandError
from django.core.urlresolvers import reverse
from selenium.webdriver.support.select import Select

from orchestra.apps.accounts.models import Account
from orchestra.apps.orchestration.models import Server, Route
from orchestra.utils.system import run
from orchestra.utils.tests import BaseLiveServerTestCase, random_ascii

from ... import backends, settings
from ...models import Satabase


class DatabaseTestMixin(object):
    MASTER_ADDR = 'localhost'
    DEPENDENCIES = (
        'orchestra.apps.orchestration',
        'orcgestra.apps.databases',
    )
    
    def setUp(self):
        super(SystemUserMixin, self).setUp()
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
        self.add()




class MysqlBackendMixin(object):
    def add_route(self):
        server = Server.objects.create(name=self.MASTER_ADDR)
        backend = backends.MysqlBackend.get_name()
        Route.objects.create(backend=backend, match="database.type == 'mysql'", host=server)
    
    def validate_create_table(self, name, username, password):
        db = MySQLdb.connect(host=self.MASTER_ADDR, user=username, passwd=password, db=name)
        cur = db.cursor()
        cur.execute('CREATE TABLE test;')
    
    def validate_delete(self, name, username, password):
        self.asseRaises(MySQLdb.ConnectionError,
                MySQLdb.connect(host=self.MASTER_ADDR, user=username, passwd=password, db=name))



class RESTDatabaseTest(DatabaseTestMixin):
    def add(self, dbname):
        self.api.databases.create(name=dbname)
